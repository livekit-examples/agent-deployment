"""KVS Managed TURN helper for LiveKit agents.

Gets temporary TURN credentials from Amazon Kinesis Video Streams
via the GetIceServerConfig API. This provides AWS-native TURN relay
without third-party dependencies.

Flow:
    1. Get or create a KVS signaling channel (cached after first call)
    2. Get the HTTPS endpoint for that channel
    3. Call GetIceServerConfig to get temporary TURN credentials
    4. Return as LiveKit rtc.IceServer objects

The signaling channel is only used for TURN credential provisioning —
LiveKit handles all actual signaling.

Cost: $0.03/month per active signaling channel.
Rate limit: GetIceServerConfig has 5 TPS per channel.
For >100K sessions/month, consider channel pooling or third-party TURN.

Environment variables:
    AWS_REGION       — AWS region (default: us-west-2)
    KVS_CHANNEL_NAME — Signaling channel name (default: livekit-agent-turn)

Required IAM permissions:
    kinesisvideo:DescribeSignalingChannel
    kinesisvideo:CreateSignalingChannel
    kinesisvideo:GetSignalingChannelEndpoint
    kinesisvideo:GetIceServerConfig
"""

import logging
import os
from typing import Optional

import boto3
from livekit import rtc

logger = logging.getLogger("kvs-turn")

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
CHANNEL_NAME = os.getenv("KVS_CHANNEL_NAME", "livekit-agent-turn")

_cached_channel_arn: Optional[str] = None
_cached_https_endpoint: Optional[str] = None


def _get_or_create_channel() -> str:
    """Get existing or create new KVS signaling channel. Returns ARN."""
    global _cached_channel_arn
    if _cached_channel_arn:
        return _cached_channel_arn

    kvs = boto3.client("kinesisvideo", region_name=AWS_REGION)
    try:
        resp = kvs.describe_signaling_channel(ChannelName=CHANNEL_NAME)
        _cached_channel_arn = resp["ChannelInfo"]["ChannelARN"]
        logger.info("Using existing KVS channel: %s", CHANNEL_NAME)
    except kvs.exceptions.ResourceNotFoundException:
        resp = kvs.create_signaling_channel(
            ChannelName=CHANNEL_NAME, ChannelType="SINGLE_MASTER"
        )
        _cached_channel_arn = resp["ChannelARN"]
        logger.info("Created KVS signaling channel: %s", CHANNEL_NAME)

    return _cached_channel_arn


def _get_https_endpoint(channel_arn: str) -> str:
    """Get HTTPS endpoint for the signaling channel."""
    global _cached_https_endpoint
    if _cached_https_endpoint:
        return _cached_https_endpoint

    kvs = boto3.client("kinesisvideo", region_name=AWS_REGION)
    resp = kvs.get_signaling_channel_endpoint(
        ChannelARN=channel_arn,
        SingleMasterChannelEndpointConfiguration={
            "Protocols": ["HTTPS"],
            "Role": "MASTER",
        },
    )
    _cached_https_endpoint = resp["ResourceEndpointList"][0]["ResourceEndpoint"]
    return _cached_https_endpoint


def get_kvs_ice_servers() -> list[rtc.IceServer]:
    """Get TURN ICE servers from KVS.

    Returns LiveKit rtc.IceServer objects with temporary credentials.
    Only TURN URIs are returned (STUN filtered — not useful behind NAT).
    """
    channel_arn = _get_or_create_channel()
    endpoint = _get_https_endpoint(channel_arn)

    signaling = boto3.client(
        "kinesis-video-signaling",
        region_name=AWS_REGION,
        endpoint_url=endpoint,
    )
    resp = signaling.get_ice_server_config(
        ChannelARN=channel_arn, Service="TURN"
    )

    ice_servers = []
    for server in resp["IceServerList"]:
        turn_urls = [u for u in server["Uris"] if u.startswith("turn:")]
        if turn_urls:
            ice_servers.append(
                rtc.IceServer(
                    urls=turn_urls,
                    username=server.get("Username", ""),
                    credential=server.get("Password", ""),
                )
            )

    logger.info("Got %d TURN server(s) from KVS channel '%s'", len(ice_servers), CHANNEL_NAME)
    return ice_servers
