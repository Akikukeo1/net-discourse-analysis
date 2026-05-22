from pathlib import Path

from nda import cli


def test_cache_path_is_not_under_package_directory() -> None:
    """ベンチマークキャッシュがパッケージ配下に保存されないことを確認する。"""
    package_dir = Path(cli.__file__).resolve().parent
    assert cli.CACHE_PATH.is_absolute()
    assert package_dir not in cli.CACHE_PATH.parents
    assert cli.CACHE_PATH.name == "benchmark_result.yaml"
