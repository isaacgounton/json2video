from abc import abstractmethod
from enum import Enum

from moviepy import ImageClip, VideoFileClip, clips_array, TextClip
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Union, Literal, override

from src.effects import EFFECT_REGISTRY
from src.utils import download_file


class TransitionType(str, Enum):
    CROSSFADE = "crossfade"
    SLIDE = "slide"
    BLINK = "blink"


class Transition(BaseModel):
    type: TransitionType = TransitionType.CROSSFADE
    duration: float = 0.5


class Effects(BaseModel):
    zoom: Optional[float] = None
    rotate: Optional[float] = None
    slidein: Optional[float] = None


class ClipBase(BaseModel):
    type: Literal["image", "split", "video"]
    duration: float
    effects: Optional[Effects] = None

    @abstractmethod
    def compile(self):
        pass

    def apply_effects(self, clip, effects):
        if self.effects:
            for effect_name, value in self.effects.model_dump().items():
                if value is not None and effect_name in EFFECT_REGISTRY:
                    clip = EFFECT_REGISTRY[effect_name](clip, value)
        return clip


class ImageItem(ClipBase):
    type: Literal["image"] = "image"
    url: HttpUrl

    @override
    def compile(self) -> ImageClip:
        img_path = download_file(self.url)
        clip = ImageClip(img_path).with_duration(self.duration)
        if self.effects:
            clip = self.apply_effects(clip, self.effects)
        return clip


class SplitItem(ClipBase):
    type: Literal["split"] = "split"
    top_url: HttpUrl
    bot_url: HttpUrl

    def make_split_screen(self, final_size: tuple[int, int] | None = None) -> ImageClip:
        def middle_half(clip: ImageClip, w: int, h: int) -> ImageClip:
            y1 = int(0.1 * h)
            y2 = int(0.6 * h)
            return clip.cropped(x1=0, y1=y1, x2=w, y2=y2)

        top_path = download_file(self.top_url)
        if final_size is not None:
            W, H = final_size
            top = middle_half(ImageClip(top_path), W, H)
        else:
            top = ImageClip(top_path)
            W, H = top.size
            top = middle_half(top, W, H)

        top = top.with_duration(self.duration)
        # load & resize bottom
        bot_path = download_file(self.bot_url)
        bot = middle_half(ImageClip(bot_path).with_duration(self.duration), W, H)
        # stack vertically
        return clips_array([[top], [bot]], bg_color=(0, 0, 0)).with_duration(
            self.duration
        )

    @override
    def compile(self) -> ImageClip:
        clip = self.make_split_screen()
        if self.effects:
            clip = self.apply_effects(clip, self.effects)
        return clip


class VideoItem(ClipBase):
    type: Literal["video"] = "video"
    url: HttpUrl
    start_time: Optional[float] = 0.0  # Start time to extract from video
    end_time: Optional[float] = None   # End time to extract from video

    @override
    def compile(self) -> VideoFileClip:
        video_path = download_file(self.url)
        clip = VideoFileClip(video_path)
        
        # Extract subclip if start_time or end_time specified
        if self.end_time is not None:
            clip = clip.subclipped(self.start_time, self.end_time)
        elif self.start_time and self.start_time > 0:
            clip = clip.subclipped(self.start_time, self.start_time + self.duration)
        
        # Set duration if specified
        clip = clip.with_duration(self.duration)
        
        if self.effects:
            clip = self.apply_effects(clip, self.effects)
        return clip

ClipItem = ImageItem | SplitItem | VideoItem


class TextOverlay(BaseModel):
    text: str
    start: float
    end: float | None = None
    position: Optional[str] = "center"
    fontsize: Optional[int] = 32
    color: Optional[str] = "white"

    def compile(self, base_clip: ImageClip) -> ImageClip:
        txt = TextClip(
            font="fonts/Impact.ttf",
            text=self.text,
            font_size=self.fontsize,
            color=self.color,
            text_align="center",
            method="caption",
            size=(base_clip.w, base_clip.h),
        )

        return txt.with_start(self.start).with_duration(
            (self.end - self.start) if self.end else base_clip.duration
        )


class VideoRequest(BaseModel):
    timeline: List[ClipItem]
    audio: Optional[HttpUrl] = None
    transition: Optional[Transition] = Field(default_factory=Transition)
    text_overlays: List[TextOverlay] = Field(default_factory=list)


class VideoResponse(BaseModel):
    url: HttpUrl
