import re

from program.settings.manager import settings_manager as sm
from program.versions.rank_models import BaseRankingModel

SETTINGS = sm.settings.ranking
CUSTOM_RANKS = sm.settings.ranking.custom_ranks
SETTINGS.compile_patterns()


def calculate_ranking(parsed_data, ranking: BaseRankingModel) -> int:
    """Calculate the ranking of a given ParsedMediaItem"""
    rank = calculate_resolution_rank(parsed_data, ranking)
    rank += calculate_quality_rank(parsed_data, ranking)
    rank += calculate_codec_rank(parsed_data, ranking)
    rank += calculate_audio_rank(parsed_data, ranking)
    rank += calculate_other_ranks(parsed_data, ranking)
    rank += calculate_preferred(parsed_data)
    if parsed_data.repack:
        rank += (
            ranking.repack
            if not CUSTOM_RANKS["repack"].enable
            else CUSTOM_RANKS["repack"].rank
        )
    if parsed_data.proper:
        rank += (
            ranking.proper
            if not CUSTOM_RANKS["proper"].enable
            else CUSTOM_RANKS["proper"].rank
        )
    if parsed_data.remux:
        rank += (
            ranking.remux
            if not CUSTOM_RANKS["remux"].enable
            else CUSTOM_RANKS["remux"].rank
        )
    if parsed_data.is_multi_audio:
        rank += (
            ranking.dubbed
            if not CUSTOM_RANKS["dubbed"].enable
            else CUSTOM_RANKS["dubbed"].rank
        )
    if parsed_data.is_multi_subtitle:
        rank += (
            ranking.subbed
            if not CUSTOM_RANKS["subbed"].enable
            else CUSTOM_RANKS["subbed"].rank
        )
    return rank


def calculate_resolution_rank(parsed_data, ranking: BaseRankingModel) -> int:
    """Calculate the resolution ranking of a given ParsedMediaItem"""
    resolution: str = parsed_data.resolution[0] if parsed_data.resolution else None
    if not resolution:
        return 0

    if parsed_data.is_4k:
        return (
            ranking.uhd if not CUSTOM_RANKS["uhd"].enable else CUSTOM_RANKS["uhd"].rank
        )

    match resolution:
        case "1080p":
            return (
                ranking.fhd
                if not CUSTOM_RANKS["fhd"].enable
                else CUSTOM_RANKS["fhd"].rank
            )
        case "720p":
            return (
                ranking.hd if not CUSTOM_RANKS["hd"].enable else CUSTOM_RANKS["hd"].rank
            )
        case "576p" | "480p":
            return (
                ranking.sd if not CUSTOM_RANKS["sd"].enable else CUSTOM_RANKS["sd"].rank
            )
        case _:
            return 0


def calculate_quality_rank(parsed_data, ranking: BaseRankingModel) -> int:
    """Calculate the quality ranking of a given ParsedMediaItem"""
    quality = parsed_data.quality[0] if parsed_data.quality else None
    if not quality:
        return 0

    match quality:
        case "WEB-DL":
            return (
                ranking.webdl
                if not CUSTOM_RANKS["webdl"].enable
                else CUSTOM_RANKS["webdl"].rank
            )
        case "Blu-ray":
            return (
                ranking.bluray
                if not CUSTOM_RANKS["bluray"].enable
                else CUSTOM_RANKS["bluray"].rank
            )
        case (
            "WEBCap"
            | "Cam"
            | "Telesync"
            | "Telecine"
            | "Screener"
            | "VODRip"
            | "TVRip"
            | "DVD-R"
        ):
            return -1000
        case "BDRip":
            return 5  # This one's a little better than BRRip
        case "BRRip":
            return 0
        case _:
            return 0


def calculate_codec_rank(parsed_data, ranking: BaseRankingModel) -> int:
    """Calculate the codec ranking of a given ParsedMediaItem"""
    codec = parsed_data.codec[0] if parsed_data.codec else None
    if not codec:
        return 0

    match codec:
        case "Xvid" | "H.263" | "VC-1" | "MPEG-2":
            return -1000
        case "AV1":
            return (
                ranking.av1
                if not CUSTOM_RANKS["av1"].enable
                else CUSTOM_RANKS["av1"].rank
            )
        case "H.264":
            return 3
        case "H.265" | "H.265 Main 10" | "HEVC":
            return 0
        case _:
            return 0


def calculate_audio_rank(parsed_data, ranking: BaseRankingModel) -> int:
    """Calculate the audio ranking of a given ParsedMediaItem"""
    audio_format: str = parsed_data.audio[0] if parsed_data.audio else None
    if not audio_format:
        return 0

    # Remove any unwanted audio formats. We dont support surround sound formats yet.
    # These also make it harder to compare audio formats.
    audio_format = re.sub(r"7.1|5.1|Dual|Mono|Original|LiNE", "", audio_format).strip()

    match audio_format:
        case "Dolby TrueHD":
            return (
                ranking.truehd
                if not CUSTOM_RANKS["truehd"].enable
                else CUSTOM_RANKS["truehd"].rank
            )
        case "Dolby Atmos":
            return (
                ranking.atmos
                if not CUSTOM_RANKS["atmos"].enable
                else CUSTOM_RANKS["atmos"].rank
            )
        case "Dolby Digital":
            return (
                ranking.ac3
                if not CUSTOM_RANKS["ac3"].enable
                else CUSTOM_RANKS["ac3"].rank
            )
        case "Dolby Digital EX":
            return (
                ranking.dts_x
                if not CUSTOM_RANKS["dts_x"].enable
                else CUSTOM_RANKS["dts_x"].rank
            )
        case "Dolby Digital Plus":
            return (
                ranking.ddplus
                if not CUSTOM_RANKS["ddplus"].enable
                else CUSTOM_RANKS["ddplus"].rank
            )
        case "DTS":
            return (
                ranking.dts_hd
                if not CUSTOM_RANKS["dts_hd"].enable
                else CUSTOM_RANKS["dts_hd"].rank
            )
        case "DTS-HD":
            return (
                (ranking.dts_hd + 5)
                if not CUSTOM_RANKS["dts_hd"].enable
                else CUSTOM_RANKS["dts_hd"].rank
            )
        case "DTS-HD MA":
            return (
                (ranking.dts_hd_ma + 10)
                if not CUSTOM_RANKS["dts_hd_ma"].enable
                else CUSTOM_RANKS["dts_hd_ma"].rank
            )
        case "DTS-ES" | "DTS-EX":
            return (
                (ranking.dts_x + 5)
                if not CUSTOM_RANKS["dts_x"].enable
                else CUSTOM_RANKS["dts_x"].rank
            )
        case "DTS:X":
            return (
                (ranking.dts_x + 10)
                if not CUSTOM_RANKS["dts_x"].enable
                else CUSTOM_RANKS["dts_x"].rank
            )
        case "AAC":
            return (
                ranking.aac
                if not CUSTOM_RANKS["aac"].enable
                else CUSTOM_RANKS["aac"].rank
            )
        case "AAC-LC":
            return (
                (ranking.aac + 2)
                if not CUSTOM_RANKS["aac"].enable
                else CUSTOM_RANKS["aac"].rank
            )
        case "HE-AAC":
            return (
                (ranking.aac + 5)
                if not CUSTOM_RANKS["aac"].enable
                else CUSTOM_RANKS["aac"].rank
            )
        case "HE-AAC v2":
            return (
                (ranking.aac + 10)
                if not CUSTOM_RANKS["aac"].enable
                else CUSTOM_RANKS["aac"].rank
            )
        case "AC3":
            return (
                ranking.ac3
                if not CUSTOM_RANKS["ac3"].enable
                else CUSTOM_RANKS["ac3"].rank
            )
        case "FLAC" | "OGG":
            return -1000
        case _:
            return 0


def calculate_other_ranks(parsed_data, ranking: BaseRankingModel) -> int:
    """Calculate all the other rankings of a given ParsedMediaItem"""
    total_rank = 0
    if parsed_data.bitDepth and parsed_data.bitDepth[0] > 8:
        total_rank += 10
    if parsed_data.hdr:
        if parsed_data.hdr == "HDR":
            total_rank += (
                CUSTOM_RANKS["hdr"].rank if CUSTOM_RANKS["hdr"].enable else ranking.hdr
            )
        elif parsed_data.hdr == "HDR10+":
            total_rank += (
                CUSTOM_RANKS["hdr10"].rank
                if CUSTOM_RANKS["hdr10"].enable
                else ranking.hdr10
            )
        elif parsed_data.hdr == "DV":
            total_rank += (
                CUSTOM_RANKS["dolby_video"].rank
                if CUSTOM_RANKS["dolby_video"].enable
                else ranking.dolby_video
            )
    if parsed_data.is_complete:
        total_rank += 100
    if parsed_data.season:
        total_rank += 100 * len(parsed_data.season)
    if parsed_data.episode:
        total_rank += 10 * len(parsed_data.episode)
    return total_rank


def calculate_preferred(parsed_data) -> int:
    """Calculate the preferred ranking of a given ParsedMediaItem"""
    if not SETTINGS.preferred or all(pattern is None for pattern in SETTINGS.preferred):
        return 0
    return (
        5000
        if any(
            pattern.search(parsed_data.raw_title)
            for pattern in SETTINGS.preferred
            if pattern
        )
        else 0
    )
