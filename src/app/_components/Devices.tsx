"use client";

import Image from "next/image";
import { PosterPlay, useBandVideo } from "./BandVideo";
import LoopVideo from "./LoopVideo";
import Phone from "./Phone";

export type Shot = { src: string; w: number; h: number; alt: string };

// The site at desktop width in a browser window, with the same product on a phone standing in front
// of its corner. With a video, the window's view is fixed at 16:9 so the demo can play in exactly the
// screenshot's place: the phone steps out of the way and nothing around it moves. Nothing from
// YouTube loads before the play button on the screenshot is pressed. The bar shows the site's public
// address, and stays empty for a project that isn't deployed. A desktop tool shows its side panel in
// the phone's place.
export default function Devices({
  url,
  desktop,
  phone,
  side,
  video,
}: {
  url?: string;
  desktop: Shot;
  phone?: Shot | { loop: string; poster: string; label: string };
  side?: Shot;
  video?: { id: string; title: string; label: string };
}) {
  const band = useBandVideo();
  const playing = Boolean(video && band?.playing);

  return (
    <div
      className="lf-devices"
      data-phone={phone ? "" : undefined}
      data-side={side ? "" : undefined}
      data-playing={playing ? "" : undefined}
    >
      <div className="lf-browser">
        <div className="lf-browser-bar" aria-hidden>
          <span className="lf-browser-dots" />
          {url && <span className="lf-browser-url">{url}</span>}
        </div>
        <div className="lf-browser-view" data-video={video ? "" : undefined}>
          <Image src={desktop.src} width={desktop.w} height={desktop.h} alt={desktop.alt} sizes="(max-width: 760px) 92vw, 52vw" />
          {video && playing && (
            <iframe
              src={`https://www.youtube-nocookie.com/embed/${video.id}?autoplay=1&rel=0&controls=0&playsinline=1&iv_load_policy=3`}
              title={video.title}
              allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
              allowFullScreen
            />
          )}
          {video && <PosterPlay label={video.label} />}
        </div>
      </div>
      {side && (
        <div className="lf-side">
          <Image src={side.src} width={side.w} height={side.h} alt={side.alt} sizes="(max-width: 760px) 26vw, 13vw" />
        </div>
      )}
      {phone && (
        <Phone>
          {"loop" in phone ? (
            <LoopVideo src={phone.loop} poster={phone.poster} label={phone.label} />
          ) : (
            <Image src={phone.src} width={phone.w} height={phone.h} alt={phone.alt} sizes="(max-width: 760px) 26vw, 13vw" />
          )}
        </Phone>
      )}
    </div>
  );
}
