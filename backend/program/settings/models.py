"""Iceberg settings models"""
from pathlib import Path
from typing import Callable, Dict

from pydantic import BaseModel, field_validator
from RTN.models import CustomRank, SettingsModel
from utils import version_file_path


class Observable(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    _notify_observers: Callable = None

    @classmethod
    def set_notify_observers(cls, notify_observers_callable):
        cls._notify_observers = notify_observers_callable

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if self.__class__._notify_observers:
            self.__class__._notify_observers()


class DebridModel(Observable):
    api_key: str = ""


class SymlinkModel(Observable):
    rclone_path: Path = Path()
    library_path: Path = Path()


# Content Services


class Updatable(Observable):
    update_interval: int = 80

    @field_validator("update_interval")
    def check_update_interval(cls, v):
        if v < (limit := 5):
            raise ValueError(f"update_interval must be at least {limit} seconds")
        return v


class PlexLibraryModel(Updatable):
    update_interval: int = 120
    token: str = ""
    url: str = "http://localhost:32400"


class ListrrModel(Updatable):
    enabled: bool = False
    movie_lists: list[str] = [""]
    show_lists: list[str] = [""]
    api_key: str = ""
    update_interval: int = 300


class MdblistModel(Updatable):
    enabled: bool = False
    api_key: str = ""
    lists: list[str] = [""]
    update_interval: int = 300


class OverseerrModel(Updatable):
    enabled: bool = False
    url: str = "http://localhost:5055"
    api_key: str = ""
    update_interval: int = 60


class PlexWatchlistModel(Updatable):
    enabled: bool = False
    rss: str = ""
    update_interval: int = 60


class ContentModel(Observable):
    listrr: ListrrModel = ListrrModel()
    mdblist: MdblistModel = MdblistModel()
    overseerr: OverseerrModel = OverseerrModel()
    plex_watchlist: PlexWatchlistModel = PlexWatchlistModel()


# Scraper Services


class JackettConfig(Observable):
    enabled: bool = False
    url: str = "http://localhost:9117"
    api_key: str = ""


class OrionoidConfig(Observable):
    enabled: bool = False
    api_key: str = ""
    limitcount: int = 5


class TorrentioConfig(Observable):
    enabled: bool = False
    filter: str = "sort=qualitysize%7Cqualityfilter=480p,scr,cam"
    url: str = "https://torrentio.strem.fun"


class AnnatarConfig(Observable):
    enabled: bool = False
    url: str = "https://annatar.elfhosted.com"
    limit: int = 20
    timeout: int = 10


class ScraperModel(Observable):
    after_2: float = 2
    after_5: int = 6
    after_10: int = 24
    jackett: JackettConfig = JackettConfig()
    orionoid: OrionoidConfig = OrionoidConfig()
    torrentio: TorrentioConfig = TorrentioConfig()
    annatar: AnnatarConfig = AnnatarConfig()


# Version Ranking Model (set application defaults here!)


class RTNSettingsModel(SettingsModel, Observable):
    profile: str = "default"
    custom_ranks: Dict[str, CustomRank] = {
        "uhd": CustomRank(fetch=False, rank=120),
        "fhd": CustomRank(fetch=True, rank=90),
        "hd": CustomRank(fetch=True, rank=80),
        "sd": CustomRank(fetch=False, rank=-120),
        "bluray": CustomRank(fetch=True, rank=80),
        "hdr": CustomRank(fetch=False, rank=80),
        "hdr10": CustomRank(fetch=False, rank=90),
        "dolby_video": CustomRank(fetch=False, rank=-100),
        "dts_x": CustomRank(fetch=False, rank=0),
        "dts_hd": CustomRank(fetch=False, rank=0),
        "dts_hd_ma": CustomRank(fetch=False, rank=0),
        "atmos": CustomRank(fetch=False, rank=0),
        "truehd": CustomRank(fetch=False, rank=0),
        "ddplus": CustomRank(fetch=False, rank=0),
        "aac": CustomRank(fetch=True, rank=70),
        "ac3": CustomRank(fetch=True, rank=50),
        "remux": CustomRank(fetch=False, rank=-1000),
        "webdl": CustomRank(fetch=True, rank=90),
        "repack": CustomRank(fetch=True, rank=5),
        "proper": CustomRank(fetch=True, rank=4),
        "dubbed": CustomRank(fetch=True, rank=4),
        "subbed": CustomRank(fetch=True, rank=2),
        "av1": CustomRank(fetch=False, rank=0),
    }


# Application Settings


class IndexerModel(Observable):
    update_interval: int = 60 * 60


def get_version() -> str:
    with open(version_file_path.resolve()) as file:
        return file.read()


class AppModel(Observable):
    version: str = get_version()
    debug: bool = True
    log: bool = True
    plex: PlexLibraryModel = PlexLibraryModel()
    real_debrid: DebridModel = DebridModel()
    symlink: SymlinkModel = SymlinkModel()
    content: ContentModel = ContentModel()
    scraping: ScraperModel = ScraperModel()
    ranking: RTNSettingsModel = RTNSettingsModel()
    indexer: IndexerModel = IndexerModel()
