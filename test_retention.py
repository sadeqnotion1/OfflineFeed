"""
Self-test for cache_retention.py -- proves the 14-day archive/restore logic on a
throwaway fixture (no network, no real repo needed). Run: python3 test_retention.py
"""
import os
import json
import time
import tempfile
import zipfile

import cache_retention as cr


def _write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


def main():
    tmp = tempfile.mkdtemp(prefix="offlinefeed_test_")
    assets = os.path.join(tmp, "offline_viewer", "assets")
    # Point the module at our throwaway tree.
    cr.ASSETS_DIR = assets
    cr.CACHED_ARTICLES_DIR = os.path.join(assets, "cached_articles")
    cr.CACHED_IMAGES_DIR = os.path.join(assets, "cached_images")
    cr.ARCHIVE_DIR = os.path.join(assets, "cache_archive")
    cr.ARCHIVE_ZIP = os.path.join(cr.ARCHIVE_DIR, "archived_posts.zip")
    cr.SNAPSHOT_PATH = os.path.join(assets, "feed_cache.json")
    cr.ARCHIVED_POSTS_PATH = os.path.join(assets, "archived_posts.json")
    cr.SAVED_POSTS_PATH = os.path.join(assets, "saved_posts.json")

    os.makedirs(cr.CACHED_ARTICLES_DIR, exist_ok=True)
    os.makedirs(cr.CACHED_IMAGES_DIR, exist_ok=True)

    now = time.time()
    old_ts = now - 20 * 86400   # 20 days old -> should archive
    new_ts = now - 2 * 86400    # 2 days old  -> should stay

    old_url = "https://example.com/old-post"
    new_url = "https://example.com/new-post"

    old_md5 = cr._md5(old_url)
    new_md5 = cr._md5(new_url)

    # in-article image unique to the OLD post
    old_img = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.jpg"
    # a shared image also used by the NEW post (must survive)
    shared_img = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb.jpg"
    # a list thumbnail for the old post (must survive: still shown in lists)
    thumb_img = "cccccccccccccccccccccccccccccccc.jpg"

    for name in (old_img, shared_img, thumb_img):
        with open(os.path.join(cr.CACHED_IMAGES_DIR, name), "wb") as f:
            f.write(b"\xff\xd8\xff" + b"x" * 100)  # fake jpeg bytes

    _write_json(os.path.join(cr.CACHED_ARTICLES_DIR, old_md5 + ".json"), {
        "title": "Old", "url": old_url,
        "blocks": [
            {"type": "p", "content": "old body"},
            {"type": "img", "content": "assets/cached_images/" + old_img},
            {"type": "img", "content": "assets/cached_images/" + shared_img},
        ],
    })
    _write_json(os.path.join(cr.CACHED_ARTICLES_DIR, new_md5 + ".json"), {
        "title": "New", "url": new_url,
        "blocks": [
            {"type": "img", "content": "assets/cached_images/" + shared_img},
        ],
    })

    # publish times + a list thumbnail for the old post, via the snapshot
    _write_json(cr.SNAPSHOT_PATH, {"articles": [
        {"url": old_url, "timestamp": old_ts,
         "thumbnail": "assets/cached_images/" + thumb_img},
        {"url": new_url, "timestamp": new_ts,
         "thumbnail": "assets/cached_images/" + shared_img},
    ]})

    stats = cr.run_retention(max_age_days=14, now=now)
    print("stats:", stats)

    a_dir = cr.CACHED_ARTICLES_DIR
    i_dir = cr.CACHED_IMAGES_DIR

    assert stats["archived"] == 1, "expected exactly 1 archived post"
    assert not os.path.exists(os.path.join(a_dir, old_md5 + ".json")), "old json should be deleted"
    assert os.path.exists(os.path.join(a_dir, new_md5 + ".json")), "new json must stay"
    assert not os.path.exists(os.path.join(i_dir, old_img)), "old unique image should be deleted"
    assert os.path.exists(os.path.join(i_dir, shared_img)), "shared image must survive"
    assert os.path.exists(os.path.join(i_dir, thumb_img)), "list thumbnail must survive"

    with zipfile.ZipFile(cr.ARCHIVE_ZIP, "r") as zf:
        names = set(zf.namelist())
    assert "cached_articles/" + old_md5 + ".json" in names, "old json must be in zip"
    assert "cached_images/" + old_img in names, "old image must be in zip"

    # restore should re-inflate the loose json + its archived image
    os.remove(os.path.join(i_dir, old_img)) if os.path.exists(os.path.join(i_dir, old_img)) else None
    ok = cr.restore_article(old_url)
    assert ok, "restore should succeed"
    assert os.path.exists(os.path.join(a_dir, old_md5 + ".json")), "json restored"
    assert os.path.exists(os.path.join(i_dir, old_img)), "image restored from zip"

    # second run must be a no-op for the (now restored but still old) post? It will
    # re-archive it -- that's fine and idempotent (zip already has the entries).
    stats2 = cr.run_retention(max_age_days=14, now=now)
    print("stats2:", stats2)

    print("ALL RETENTION TESTS PASSED")


if __name__ == "__main__":
    main()
