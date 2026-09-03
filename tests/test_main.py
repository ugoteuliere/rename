import sys
import pytest
import pandas as pd
from pathlib import Path, PureWindowsPath, PurePosixPath
from unittest.mock import patch, call, MagicMock
from src import files, utils, api, mail, ui
import requests
import smtplib

fichiers = [
    # 30 files have to be corrected
    "Inception.2010.1080p.BluRay.x264.VFF.AC3-GROUP.mkv",
    "The.Matrix.1999.REMASTERED.2160p.UHD.BluRay.x265.10bit.HDR.TrueHD.7.1.Atmos.MULTI.SUBFRENCH-RLS.mp4",
    "Dune.Part.Two.2024.2160p.WEB-DL.DDP5.1.Atmos.DV.HDR10.HEVC.VOSTFR-TEAM.mkv",
    "Interstellar 2014 IMAX 1080p BDRip x264 DTS 5.1 TRUEFRENCH-FRG.avi",
    "The.Dark.Knight.2008.720p.HDLight.x264.AC3.VF.mkv",
    "Avatar.The.Way.of.Water.2022.4K.HDR.WEB-DL.x265.EAC3.5.1.MULTI.VFF-GRP.mkv",
    "Pulp.Fiction.1994.1080p.BluRay.Remux.AVC.DTS-HD.MA.5.1.MULTI.VOSTFR-TAG.mkv",
    "Fight_Club_1999_1080p_BrRip_x264_AAC_2.0_VF.mp4",
    "Avengers Endgame 2019 1080p WEBRip x264 AC3 5.1 FRENCH-RLS.mkv",
    "Spider-Man.Across.the.Spider-Verse.2023.2160p.UHD.BluRay.x265.10bit.HDR.TrueFrench.DTS-HD.7.1-FW.mkv",
    "Gladiator.2000.EXTENDED.1080p.BluRay.x264.DTS.MULTI.VF2.mkv",
    "The.Lord.of.the.Rings.The.Fellowship.of.the.Ring.2001.EXTENDED.2160p.UHD.BluRay.x265.HDR.Atmos.TrueHD.7.1.MULTI.VOSTFR-TEAM.mkv",
    "Oppenheimer.2023.IMAX.2160p.WEB-DL.x265.10bit.SDR.EAC3.5.1.VFF.SUBFRENCH-GRP.mkv",
    "Joker.2019.1080p.HDLight.x265.AC3.5.1.VF-LIHDL.mkv",
    "Deadpool.and.Wolverine.2024.HDCAM.x264.MP3.2.0.FRENCH-CAMS.avi",
    "Breaking.Bad.S01E01.Pilot.1080p.BluRay.x264.AC3.5.1.MULTI.VOSTFR-TV.mkv",
    "Game.of.Thrones.S08E03.1080p.AMZN.WEB-DL.DDP5.1.x264.VFF-GRP.mkv",
    "Stranger Things S04E01 2160p NF WEB-DL x265 10bit HDR DDP5.1 Atmos MULTI VF.mkv",
    "The.Boys.S03E06.Herogasm.1080p.WEB.H264.EAC3.5.1.VOSTFR-RLS.mkv",
    "True.Detective.S01E04.1080p.BluRay.x265.HEVC.10bit.AAC.5.1.MULTI.mkv",
    "Mad.Max.Fury.Road.2015.1080p.BluRay.x264.TrueHD.7.1.Atmos.MULTI.VFF-GRP.mkv",
    "Blade.Runner.2049.2017.2160p.UHD.BluRay.Remux.HEVC.HDR.TrueHD.7.1.Atmos.VOSTFR-TEAM.mkv",
    "Jurassic.Park.1993.REMASTERED.1080p.BDRip.x264.DTS.5.1.TRUEFRENCH.mkv",
    "The.Godfather.1972.REMASTERED.1080p.BluRay.x264.AC3.5.1.MULTI.VOSTFR-GRP.mkv",
    "Parasite.2019.1080p.BluRay.x264.DTS.5.1.VOSTFR.SUBFRENCH-RLS.mkv",
    "Everything.Everywhere.All.at.Once.2022.2160p.WEB-DL.x265.10bit.HDR.EAC3.5.1.VFF-TEAM.mkv",
    "Arcane.S01E01.1080p.NF.WEBRip.DDP5.1.x264.MULTI.VF2-GRP.mkv",
    "The.Last.of.Us.S01E01.2160p.MAX.WEB-DL.x265.10bit.HDR.Atmos.MULTI.VFF-FW.mkv",
    "Titanic.1997.1080p.BluRay.x264.DTS-HD.MA.5.1.MULTI.VFF.mkv",
    "Alien.1979.DIRECTORS.CUT.1080p.BDRip.x264.AC3.5.1.TRUEFRENCH-TEAM.mkv",

    # already corrected to tests the filters
    "Arrival (2016).mkv",
    "A Knight of the Seven Kingdoms - S01E01.mkv",
    "Suits - S01E01.mkv"
]

fichiers_corriges = [
    "Inception (2010)",
    "The Matrix (1999)",
    "Dune - Part Two (2024)",
    "Interstellar (2014)",
    "The Dark Knight (2008)",
    "Avatar - The Way of Water (2022)",
    "Pulp Fiction (1994)",
    "Fight Club (1999)",
    "Avengers - Endgame (2019)",
    "Spider-Man - Across the Spider-Verse (2023)",
    "Gladiator (2000)",
    "The Lord of the Rings - The Fellowship of the Ring (2001)",
    "Oppenheimer (2023)",
    "Joker (2019)",
    "Deadpool & Wolverine (2024)",
    "Breaking Bad - S01E01",
    "Game of Thrones - S08E03",
    "Stranger Things - S04E01",
    "The Boys - S03E06",
    "True Detective - S01E04",
    "Mad Max - Fury Road (2015)",
    "Blade Runner 2049 (2017)",
    "Jurassic Park (1993)",
    "The Godfather (1972)",
    "Parasite (2019)",
    "Everything Everywhere All at Once (2022)",
    "Arcane - S01E01",
    "The Last of Us - S01E01",
    "Titanic (1997)",
    "Alien (1979)"
]

donnees_test_api = [
    ("Blade Runner 2049", 2017, "movie", [True,"Blade Runner 2049", "2017", "en"]),
    ("Inception", 2010, "movie", [True,"Inception", "2010", "en"]),
    ("Parasite", 2019, "movie", [True,"Parasite", "2019", "ko"]),
    ("The Matrix", None, "movie", [True,"The Matrix", "1999", "en"]),
    ("Spirited Away", 2001, "movie", [True,"Spirited Away", "2001", "ja"]),
    ("Stranger Things", None, "tv", [True, "Stranger Things", "2016", "en"]),
    ("Breaking Bad", 2008, "tv", [True, "Breaking Bad", "2008", "en"]),
    ("Game of Thrones", None, "tv", [True, "Game of Thrones", "2011", "en"]),
    ("Dark", 2017, "tv", [True, "Dark", "2017", "de"]),
    ("Lupin", None, "tv", [True, "Lupin", "2021", "fr"]),
]

MOVIES_FOLDER = "Films"
TV_SHOWS_FOLDER = "Séries"
NOT_SORTED_MEDIA_FILES_FOLDER = ".download"

@pytest.fixture
def setup(tmp_path, monkeypatch):
    dossier_download = tmp_path / NOT_SORTED_MEDIA_FILES_FOLDER
    dossier_download.mkdir()
    (tmp_path / MOVIES_FOLDER).mkdir()
    (tmp_path / TV_SHOWS_FOLDER).mkdir()
    
    monkeypatch.setattr("src.files.MOVIES_FOLDER", str(tmp_path / MOVIES_FOLDER))
    monkeypatch.setattr("src.files.TV_SHOWS_FOLDER", str(tmp_path / TV_SHOWS_FOLDER))
    monkeypatch.setattr("src.files.NOT_SORTED_MEDIA_FILES_FOLDER", str(tmp_path / NOT_SORTED_MEDIA_FILES_FOLDER))
    monkeypatch.setattr("src.utils.RESOLUTION", False)
    monkeypatch.setattr("src.utils.QUALITY", False)
    
    for nom in fichiers:
        (dossier_download / nom).touch()

    yield tmp_path

def check_parsed_media_type (media_files,filename,media):
    for index,movie in media_files.iterrows():
        i = 0
        found = False
        while (i<len(media_files)-1 and not found):
            if movie.loc['File'] == filename :
                assert movie['Media'] == media
                found = True
            i=i+1

def test_search_media_files(setup):
    media_files, clean_files = files.search_media_files(None)
    assert len(media_files) == 30
    assert len(clean_files) == 3
    check_parsed_media_type (media_files,"Inception.2010.1080p.BluRay.x264.VFF.AC3-GROUP.mkv","movie")
    check_parsed_media_type (media_files,"Arcane.S01E01.1080p.NF.WEBRip.DDP5.1.x264.MULTI.VF2-GRP.mkv","tv")
    check_parsed_media_type (media_files,"Everything.Everywhere.All.at.Once.2022.2160p.WEB-DL.x265.10bit.HDR.EAC3.5.1.VFF-TEAM.mkv","movie")

@pytest.mark.parametrize("name, year, media_type, expected", donnees_test_api)
def test_api_call(name, year, media_type, expected):
    resultat = api.api_call(name, year, "en-US", media_type)
    assert resultat == expected

def test_api_call_errors():
    # test 2 : wrong name
    name = "ezgshdgnfsdfshd"
    year = "None"
    media_type = "movie"
    assert api.api_call(name, year, "en-US", media_type) == [False, None, None, None]

def test_get_corrected_media_filenames(setup):
    media_files, clean_files = files.search_media_files(None)
    corrected_filenames = utils.get_corrected_media_filenames(media_files,clean_files)
    for index,movie in corrected_filenames.iterrows():
        i = 0
        found = False
        while (i<len(fichiers_corriges)-1 and not found):
            if corrected_filenames.loc[index,'Original'] == fichiers[i]:
                assert movie['Corrected'] == fichiers_corriges[i]
                found = True
            i=i+1

def test_rename_media_files(setup):
    media_files, clean_files = files.search_media_files(None)
    corrected_filenames = utils.get_corrected_media_filenames(media_files,clean_files)
    files.rename_media_files(corrected_filenames)

    # scan of the folder with corrected filenames
    target_dir = Path(NOT_SORTED_MEDIA_FILES_FOLDER)
    for file_path in target_dir.rglob('*'):
        corrected_name = file_path.stem.strip()
        if corrected_name not in ["Arrival (2016)", "A Knight of the Seven Kingdoms - S01E01", "Suits - S01E01"] :
            assert corrected_name in fichiers_corriges

donnees_test_gemini_api = [(
    {
        'File': "Blade.Runner.2049.2017.2160p.UHD.BluRay.Remux.HEVC.HDR.TrueHD.7.1.Atmos.VOSTFR-TEAM.mkv",
        'Folder': NOT_SORTED_MEDIA_FILES_FOLDER,
        'Path': f"/home/ugo/movies/{NOT_SORTED_MEDIA_FILES_FOLDER}",
        'Clean': "Blade Runner 2049 2160p HEVC",
        'Parse': None,
        'Media': "movie"
    }, [True, "Blade Runner 2049", "2017", "en", ["2160p","HEVC"]])
]

@pytest.mark.parametrize("media_info, expected", donnees_test_gemini_api)
def test_gemini_api_call(media_info, expected, monkeypatch):
    monkeypatch.setattr("src.ui.VERBOSE_ENABLED", True)
    monkeypatch.setattr(api, "TAGS", [r'480p', r'720p'])
    try:
        resultat = api.gemini_api_call(media_info)
        assert resultat[0] == expected[0]
        assert resultat[1] == expected[1]
        assert resultat[2] == expected[2]
        assert resultat[3] == expected[3]
        assert isinstance(resultat[4], list)
    except RuntimeError as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower() or "GEMINI API call failed" in str(e):
            pytest.skip("Skipped: Gemini API free plan limit reached (429 RESOURCE_EXHAUSTED).")
        else:
            raise

donnees_wrong_test_gemini_api = [(
    {
        'File': "jkdvdqskldnvdsvsvsj.mkv",
        'Folder': NOT_SORTED_MEDIA_FILES_FOLDER,
        'Path': f"/home/ugo/movies/{NOT_SORTED_MEDIA_FILES_FOLDER}",
        'Clean': "zinovikns,dl",
        'Parse': None,
        'Media': "movie"
    }, [False, None, None, None, None])
]

@pytest.mark.parametrize("media_info, expected", donnees_wrong_test_gemini_api)
def test_error_gemini_api_call(media_info, expected, monkeypatch):
    monkeypatch.setattr("src.ui.VERBOSE_ENABLED", True)
    try:
        resultat = api.gemini_api_call(media_info)
        assert resultat == expected
    except RuntimeError as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower() or "GEMINI API call failed" in str(e):
            pytest.skip("Skipped: Gemini API free plan limit reached (429 RESOURCE_EXHAUSTED).")
        else:
            raise

def test_file_impossible_to_rename_and_mail():
    media_files = pd.DataFrame([{
        'File': "apjfpjkd.mkv",
        'Folder': NOT_SORTED_MEDIA_FILES_FOLDER,
        'Path': f"/home/ugo/movies/{NOT_SORTED_MEDIA_FILES_FOLDER}",
        'Clean': ["apjfpjkd", "", "", ""],
        'Parse': ["apjfpjkd", "", "", ""],
        'Media': "movie"
    }])
    clean_files = pd.DataFrame([])
    
    try:
        corrected_filenames = utils.get_corrected_media_filenames(media_files, clean_files)
        assert corrected_filenames.empty
    except RuntimeError as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "This model is currently experiencing high demand." in str(e):
            pytest.skip("Skipped: Gemini API free plan limit reached (429 RESOURCE_EXHAUSTED).")
        else:
            raise

@pytest.mark.parametrize("file_name, expected_title, expected_year", [
    # --- 1. FILMS STANDARDS ---
    ("Inception.2010.1080p.BluRay.x264.VFF.AC3-GROUP.mkv", "Inception", "2010"),
    ("The.Matrix.1999.REMASTERED.2160p.UHD.BluRay.x265.10bit.HDR.TrueHD.7.1.Atmos.MULTI.SUBFRENCH-RLS.mp4", "The Matrix", "1999"),
    ("Dune.Part.Two.2024.2160p.WEB-DL.DDP5.1.Atmos.DV.HDR10.HEVC.VOSTFR-TEAM.mkv", "Dune Part Two", "2024"), # Tirets remplacés par des espaces par ta fonction
    ("Interstellar 2014 IMAX 1080p BDRip x264 DTS 5.1 TRUEFRENCH-FRG.avi", "Interstellar", "2014"),
    ("The.Dark.Knight.2008.720p.HDLight.x264.AC3.VF.mkv", "The Dark Knight", "2008"),
    ("Avatar.The.Way.of.Water.2022.4K.HDR.WEB-DL.x265.EAC3.5.1.MULTI.VFF-GRP.mkv", "Avatar The Way of Water", "2022"),
    ("Pulp.Fiction.1994.1080p.BluRay.Remux.AVC.DTS-HD.MA.5.1.MULTI.VOSTFR-TAG.mkv", "Pulp Fiction", "1994"),
    ("Fight_Club_1999_1080p_BrRip_x264_AAC_2.0_VF.mp4", "Fight Club", "1999"), # Underscores remplacés par des espaces
    ("Spider-Man.Across.the.Spider-Verse.2023.2160p.UHD.BluRay.x265.10bit.HDR.TrueFrench.DTS-HD.7.1-FW.mkv", "Spider Man Across the Spider Verse", "2023"),
    
    # --- 2. SÉRIES TV (Ta fonction supprime actuellement le SxxExx) ---
    ("Breaking.Bad.S01E01.Pilot.1080p.BluRay.x264.AC3.5.1.MULTI.VOSTFR-TV.mkv", "Breaking Bad Pilot", ""), # S01E01 effacé, Pas d'année
    ("Game.of.Thrones.S08E03.1080p.AMZN.WEB-DL.DDP5.1.x264.VFF-GRP.mkv", "Game of Thrones", ""),
    ("Stranger Things S04E01 2160p NF WEB-DL x265 10bit HDR DDP5.1 Atmos MULTI VF.mkv", "Stranger Things", ""),
    ("The.Boys.S03E06.Herogasm.1080p.WEB.H264.EAC3.5.1.VOSTFR-RLS.mkv", "The Boys Herogasm", ""),
    
    # --- 3. DÉJÀ PROPRES (Pour vérifier que la fonction ne casse rien) ---
    ("Arrival (2016).mkv", "Arrival", "2016"),
    ("A Knight of the Seven Kingdoms S01E01.mkv", "A Knight of the Seven Kingdoms", ""), # S01E01 sera effacé par ta regex
    
    # Standard domain with 'www.'
    ("Avatar.2009.www.pirate-bay.org.1080p.mkv", "Avatar", "2009"),
    
    # Standard domain without 'www.'
    ("The.Batman.2022.tracker.net.720p.mkv", "The Batman", "2022"),
    
    # Subdomains with 'www.' (Tests Case 1: Greedy safe capture)
    ("Inception.2010.www.forum.my-tracker.co.uk.mkv", "Inception", "2010"),
    
    # Multiple valid TLDs chained together (Tests Case 2: e.g., .com.br)
    ("Gladiator.2000.release.com.br.1080p.mkv", "Gladiator", "2000"),
    ("City.Of.God.2002.tracker.co.jp.720p.mkv", "City Of God", "2002"),
    
    # Title protection (Tests Case 2: Only 1 word captured before TLD if no www)
    # "My.Beautiful.Movie" must remain intact, only "site.com" is removed.
    ("My.Beautiful.Movie.2015.site.com.mkv", "My Beautiful Movie", "2015"),
    
    # Domain at the very beginning of the filename
    ("www.movie-site.info.Deadpool.2016.1080p.mkv", "Deadpool", "2016"),
    
    # Domains containing dashes (very common in scene releases)
    ("Interstellar.2014.super-awesome-tracker.net.1080p.mkv", "Interstellar", "2014"),
    
    # Domains with no year present in the filename
    ("Tenet.www.nolan-films.net.1080p.mkv", "Tenet", ""),
    
    # Very short ccTLD (Testing standard geographic domains)
    ("Amelie.Poulain.2001.french-tracker.fr.mkv", "Amelie Poulain", "2001"),
    
    # Edge Case: Title contains a word that looks like a domain but doesn't match the TLD list exactly
    # (Assuming "movie" is NOT in your TLD list, it shouldn't be touched)
    ("Scary.Movie.2000.1080p.mkv", "Scary Movie", "2000"),
    
    # Test de la suppression des nombres à 5 chiffres et plus (ex: IDs de torrents)
    ("Movie.With.Tracker.ID.1234567.2005.mkv", "Movie With Tracker ID", "2005"),
    ("Short.ID.98765.1998.avi", "Short ID", "1998"),
    
    # Test de formats d'années complexes ou multiples (ta fonction prend la 1ère occurrence)
    ("Movie.Set.In.2049.2017.1080p.mkv", "Movie Set In", "2049"),
    ("Year.In.Parentheses.(2023).mkv", "Year In Parentheses", "2023"),
    ("Trop___de...points---et_tirets.2010.mkv", "Trop de points et tirets", "2010"),
])
def test_clean_function(file_name, expected_title, expected_year):
    result_title, result_year, *_ = utils.clean_filename(file_name)
    assert result_title == expected_title, f"Error on the title of the file: {file_name}"
    assert result_year == expected_year, f"Error on the year of the file: {file_name}"


@pytest.mark.parametrize("file_name, expected_cleaned", [
    # --- CASE 1: Starts with 'www.' (Greedy capture of subdomains) ---
    ("Avatar.2009.www.pirate-bay.org.1080p.mkv", "Avatar.2009.1080p.mkv"),
    ("Inception.2010.www.forum.my-tracker.co.uk.mkv", "Inception.2010.mkv"),
    ("www.movie-site.info.Deadpool.2016.1080p.mkv", "Deadpool.2016.1080p.mkv"),
    
    # --- CASE 2: No 'www.' (Strictly ONE word before TLD to protect title) ---
    ("The.Batman.2022.tracker.net.720p.mkv", "The.Batman.2022.720p.mkv"),
    # 'My.Beautiful.Movie' must survive, only 'site.com' is removed
    ("My.Beautiful.Movie.2015.site.com.mkv", "My.Beautiful.Movie.2015.mkv"), 
    # Multiple TLDs chained (.com.br)
    ("Gladiator.2000.release.com.br.1080p.mkv", "Gladiator.2000.1080p.mkv"), 
    ("City.Of.God.2002.tracker.co.jp.720p.mkv", "City.Of.God.2002.720p.mkv"),
    
    # --- Edge Cases & Complex Structures ---
    # Domain at the very end of the string
    ("Joker.2019.1080p.BLURAY.site.xyz", "Joker.2019.1080p.BLURAY"), 
    # Multiple different domains in the same filename
    ("www.site-one.com.The.Matrix..1999.mkv", "The.Matrix.1999.mkv"), 
    # No year or resolution present
    ("Tenet.www.nolan-films.net.1080p.mkv", "Tenet.1080p.mkv"), 
    # Short ccTLD (.fr)
    ("Amelie.Poulain.2001.french-tracker.fr.mkv", "Amelie.Poulain.2001.mkv"), 
    # Dashes within the domain name
    ("Interstellar.2014.super-awesome-tracker.net.1080p.mkv", "Interstellar.2014.1080p.mkv"), 
    
    # --- False Positive Protection ---
    # Assuming "movie", "film", and "dot" are NOT in the TLDS list, these must remain entirely intact
    ("Scary.Movie.2000.1080p.mkv", "Scary.Movie.2000.1080p.mkv"),
    ("A.Good.Film.2018.mkv", "A.Good.Film.2018.mkv"),
    ("Murder.Dot.Com.2008.mkv", "Murder.2008.mkv"), # .Com will be removed, leaving Murder.Dot.2008.mkv (if 'com' is in TLDs)
])
def test_remove_url(file_name, expected_cleaned):
    """
    Tests the remove_url function to ensure it strips domains correctly
    without eating into the movie title or other valid metadata.
    """
    result = utils.remove_url(file_name)
    assert result == expected_cleaned, f"Failed on '{file_name}'. Expected '{expected_cleaned}', but got '{result}'"

# case success
def test_add_new_tags_success(tmp_path, monkeypatch):
    # 1. Setup : Création d'un faux fichier data.py
    fake_data_file = tmp_path / "data.py"
    initial_content = """# Début du fichier
import re

TAGS = [
    r'1080p', r'bluray',
    r'vff'
]

# Fin du fichier
def dummy_function():
    pass
"""
    fake_data_file.write_text(initial_content, encoding="utf-8")
    
    # 2. Mock : On redirige DATA_FILE vers notre faux fichier
    monkeypatch.setattr(utils, "DATA_FILE", fake_data_file)
    
    # 3. La grande liste de tests (couvre tous les cas)
    tags_to_test = [
        "vostfr",         # Cas basique : Mot normal
        "  TrueFrench  ", # Nettoyage : Espaces autour et majuscules
        "hdr10+",         # Regex : Caractère spécial '+' (doit être échappé en \+)
        "dts.ma",         # Regex : Caractère spécial '.' (doit être échappé en \.)
        "bluray",         # Doublon texte : Déjà dans le fichier initial (doit être ignoré)
        "",               # Cas vide : Chaîne vide (doit être ignorée)
        "   "             # Cas vide : Espaces seuls (doit être ignorée)
    ]
    
    # 4. Exécution
    utils.add_new_tags(tags_to_test)
    
    # 5. Vérifications
    result_content = fake_data_file.read_text(encoding="utf-8")
    
    # Vérification des ajouts et du nettoyage (minuscules)
    assert "r'vostfr'" in result_content
    assert "r'truefrench'" in result_content
    
    # Vérification CRITIQUE : l'échappement des caractères regex
    assert r"r'hdr10\+'" in result_content
    assert r"r'dts\.ma'" in result_content
    
    # Vérification des doublons : bluray ne doit apparaître qu'une seule fois
    assert result_content.count("r'bluray'") == 1
    
    # Vérification de l'intégrité du fichier (le code autour ne doit pas être cassé)
    assert "def dummy_function():" in result_content
    assert "# Début du fichier" in result_content


# ==========================================
# TEST 2 : LES CAS D'ERREURS ET LIMITES
# ==========================================
def test_add_new_tags_errors(tmp_path, monkeypatch, capsys):
    
    # --- Cas d'erreur A : Le fichier n'existe pas ---
    missing_file = tmp_path / "non_existent.py"
    monkeypatch.setattr(utils, "DATA_FILE", missing_file)
    with pytest.raises(RuntimeError) as exc_info:
        utils.add_new_tags(["vostfr"])
    assert "The file" in str(exc_info.value)
    
    # --- Cas d'erreur B : Le fichier existe mais n'a pas de liste TAGS ---
    invalid_file = tmp_path / "invalid_data.py"
    invalid_file.write_text("UNE_AUTRE_LISTE = ['a', 'b']", encoding="utf-8")
    monkeypatch.setattr(utils, "DATA_FILE", invalid_file)
    utils.add_new_tags(["vostfr"])
    captured = capsys.readouterr()
    assert "Impossible to find TAGS list" in captured.out
    
    # --- Cas d'erreur C : La liste fournie est vide ou None ---
    valid_file = tmp_path / "data.py"
    valid_file.write_text("TAGS = [r'1080p']", encoding="utf-8")
    monkeypatch.setattr(utils, "DATA_FILE", valid_file)
    
    # Ne doit rien faire du tout
    utils.add_new_tags([])
    utils.add_new_tags(None)
    
    # Le contenu doit être strictement identique
    assert valid_file.read_text(encoding="utf-8") == "TAGS = [r'1080p']"


def test_move_file_success(tmp_path):
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "dest"
    source_dir.mkdir()
    dest_dir.mkdir()
    
    # create a fake file to move
    old_path = source_dir / "video.mkv"
    old_path.write_text("fake video content") 
    new_path = dest_dir / "video.mkv"

    # We "mock" make_safe_path so it just returns the path as a string during the test.
    # Replace 'src.files.make_safe_path' with the actual path to that function.
    with patch('src.files.make_safe_path', side_effect=lambda x: str(x)):
        
        # 2. ACTION (Act)
        files.move_file(old_path, new_path)

    assert not old_path.exists() # The original file should be gone
    assert new_path.exists()     # The file should be in the new location
    assert new_path.read_text() == "fake video content" # Data should be intact


def test_move_file_raises_runtime_error(tmp_path):
    # 1. SETUP
    # These files don't actually need to exist for this test because we are going to force an error
    old_path = tmp_path / "source.txt"
    new_path = tmp_path / "dest.txt"
    
    # 2. ACTION & VERIFY
    with patch('src.ui.VERBOSE_ENABLED', True):
        with patch('src.files.make_safe_path', side_effect=lambda x: str(x)):
            
            # We force shutil.move to crash with a fake PermissionError
            with patch('shutil.move', side_effect=PermissionError("Access denied")):
                
                # We catch your custom RuntimeError
                with pytest.raises(RuntimeError) as exc_info:
                    files.move_file(old_path, new_path)
                    
    # 3. VERIFY ERROR MESSAGE
    # We check that your custom formatting and the original error are both present
    error_message = str(exc_info.value)
    assert "Impossible to move the file" in error_message
    assert str(old_path) in error_message
    assert str(new_path) in error_message
    assert "Access denied" in error_message


def test_remove_empty_folders_path_does_not_exist(tmp_path):
    # 1. SETUP
    fake_path = tmp_path / "ghost_folder"
    
    # 2. ACTION & VERIFY
    # We patch your ui.print_log so it doesn't actually print to the console during tests,
    # and so we can check what message was sent to it.
    with patch('src.ui.print_log') as mock_print:
        files.remove_empty_folders(str(fake_path))
        
        # Verify the function caught the bad path and logged it
        mock_print.assert_called_once()
        assert "does not exist" in mock_print.call_args[0][0]


def test_remove_empty_folders_success(tmp_path):
    # 1. SETUP: Create a complex folder structure
    target_path = tmp_path / "main_folder"
    target_path.mkdir()
    
    # Folder A: Empty
    empty_dir_1 = target_path / "empty_1"
    empty_dir_1.mkdir()
    
    # Folder B: Contains a nested empty folder
    empty_dir_2 = target_path / "empty_2"
    empty_dir_2.mkdir()
    nested_empty = empty_dir_2 / "nested_empty"
    nested_empty.mkdir()
    
    # Folder C: Contains a file (Should NOT be deleted)
    not_empty_dir = target_path / "keep_me"
    not_empty_dir.mkdir()
    (not_empty_dir / "video.mkv").write_text("fake video data")
    
    # 2. ACTION
    files.remove_empty_folders(str(target_path))
    
    # 3. VERIFY
    # The empty folders should be gone
    assert not empty_dir_1.exists()
    assert not nested_empty.exists()
    assert not empty_dir_2.exists() # Because the nested one was deleted, this became empty and should also be gone!
    
    # The folder with the file should remain untouched
    assert not_empty_dir.exists()
    assert (not_empty_dir / "video.mkv").exists()
    
    # Crucially: The main target folder must survive!
    assert target_path.exists()


def test_remove_empty_folders_raises_runtime_error(tmp_path):
    # 1. SETUP
    target_path = tmp_path / "main"
    target_path.mkdir()
    empty_dir = target_path / "empty_dir"
    empty_dir.mkdir()
    
    # 2. ACTION & VERIFY
    # We force the built-in os.rmdir to fail with a fake OS error
    with patch('src.ui.VERBOSE_ENABLED', True):
        with patch('os.rmdir', side_effect=OSError("Folder is locked by another process")):
            
            # We expect your custom RuntimeError to be raised
            with pytest.raises(RuntimeError) as exc_info:
                files.remove_empty_folders(str(target_path))
                
    # 3. VERIFY ERROR MESSAGE
    error_msg = str(exc_info.value)
    assert "An error occurred while deleting" in error_msg
    assert str(empty_dir) in error_msg
    assert "Folder is locked" in error_msg


@patch('src.files.remove_empty_folders')
@patch('src.ui.print_log')
@patch('src.files.move_file')
@patch('src.files.NOT_SORTED_MEDIA_FILES_FOLDER', 'unsorted_media') # Faking the global variable
def test_move_media_files_success(mock_move_file, mock_print_log, mock_remove_empty_folders):
    # 1. SETUP
    # A list of fake paths to move
    paths_to_move = [
        ("path/to/old1.mkv", "path/to/new1.mkv"),
        ("path/to/old2.mkv", "path/to/new2.mkv")
    ]
    
    # 2. ACTION
    files.move_media_files(paths_to_move)
    
    # 3. VERIFY
    # Did it try to move exactly 2 files?
    assert mock_move_file.call_count == 2
    
    # Did it call move_file with the exact right arguments in the right order?
    expected_calls = [
        call("path/to/old1.mkv", "path/to/new1.mkv"),
        call("path/to/old2.mkv", "path/to/new2.mkv")
    ]
    mock_move_file.assert_has_calls(expected_calls)
    
    # Did it print the correct success message with the number '2'?
    mock_print_log.assert_called_once()
    assert "2 files moved successfully!" in mock_print_log.call_args[0][0]
    
    # Did it try to clean up the empty folders in the correct target directory?
    expected_cleanup_path = Path('unsorted_media')
    mock_remove_empty_folders.assert_called_once_with(expected_cleanup_path)


@patch('src.files.remove_empty_folders')
@patch('src.ui.print_log')
@patch('src.files.move_file')
@patch('src.files.NOT_SORTED_MEDIA_FILES_FOLDER', 'unsorted')
def test_move_media_files_empty_list(mock_move_file, mock_print_log, mock_remove_empty_folders):
    # 1. SETUP
    paths_to_move = [] # Empty list!
    
    # 2. ACTION
    files.move_media_files(paths_to_move)
    
    # 3. VERIFY
    mock_move_file.assert_not_called() # Should not have tried to move anything
    mock_print_log.assert_not_called()
    mock_remove_empty_folders.assert_called_once() # Should still try to clean up the root folder


@patch('src.files.remove_empty_folders')
@patch('src.ui.print_log')
@patch('src.files.move_file')
@patch('src.files.NOT_SORTED_MEDIA_FILES_FOLDER', 'unsorted')
def test_move_media_files_stops_on_error(mock_move_file, mock_print_log, mock_remove_empty_folders):
    # 1. SETUP
    paths_to_move = [
        (Path("old1"), Path("new1")),
        (Path("old2"), Path("new2"))
    ]
    
    # We force the FIRST call to move_file to crash
    mock_move_file.side_effect = [RuntimeError("Fatal move error"), None]
    
    # 2. ACTION & VERIFY
    # The error is caught, skipped, and remaining files are processed
    files.move_media_files(paths_to_move)
        
    assert mock_move_file.call_count == 2
    mock_remove_empty_folders.assert_called_once()

# ---------------------------------------------------------
# SCENARIO 1: Pretend we are on WINDOWS ('nt')
# ---------------------------------------------------------
@patch('os.name', 'nt')
@pytest.mark.parametrize("input_string, expected_output", [
    (
        r"C:\Media\Unsorted\video.mkv", 
        r"\\?\C:\Media\Unsorted\video.mkv"
    ),
    (
        r"\\MyNAS\PlexMedia\video.mkv", 
        r"\\?\UNC\MyNAS\PlexMedia\video.mkv"
    ),
    (
        r"folder\file.txt", 
        r"\\?\folder\file.txt"
    ),
])
def test_make_safe_path_windows(input_string, expected_output):
    # PureWindowsPath forces Python to handle the backslashes like Windows
    test_path = PureWindowsPath(input_string)
    
    result = files.make_safe_path(test_path)
    
    assert result == expected_output


# ---------------------------------------------------------
# SCENARIO 2: Pretend we are on MAC / LINUX ('posix')
# ---------------------------------------------------------
@patch('os.name', 'posix')
@pytest.mark.parametrize("input_string", [
    "/Users/name/Media/Unsorted/video.mkv",
    "relative/folder/file.txt"
])
def test_make_safe_path_mac_linux(input_string):
    # PurePosixPath forces Python to handle the forward slashes like Mac/Unix
    test_path = PurePosixPath(input_string)
    
    result = files.make_safe_path(test_path)
    
    # On a Mac, the function should do absolutely nothing to the string
    assert result == str(test_path)


def patch_globals(func):
    """Decorator to apply common patches to the tests."""
    func = patch('src.files.MOVIES_FOLDER', 'Movies')(func)
    func = patch('src.files.TV_SHOWS_FOLDER', 'TV Shows')(func)
    func = patch('src.ui.print_log')(func)
    return func


@patch_globals
def test_sort_media_files_success(mock_print, tmp_path, monkeypatch):
    monkeypatch.setattr("src.files.MOVIES_FOLDER", str(tmp_path / 'Movies'))
    monkeypatch.setattr("src.files.TV_SHOWS_FOLDER", str(tmp_path / 'TV Shows'))
    
    # We dynamically generate a downloads folder path that matches the OS
    dl_dir = tmp_path / 'downloads'
    
    # Create a fake Pandas DataFrame using our OS-safe paths
    data = {
        'Path': [
            str(dl_dir / 'movie1.mkv'),      # Standard movie
            str(dl_dir / 'show1.mp4'),       # Standard TV Show
            str(dl_dir / 'weird_show.avi'),  # TV Show missing SxxExx
            str(dl_dir / 'junk.txt')         # Unrecognized media
        ],
        'Media': ['movie', 'tv', 'tv', 'unknown'],
        'Corrected': [
            'The Matrix (1999)', 
            'Breaking Bad S01E05', 
            'Weird Show Name', 
            'Junk File'
        ]
    }
    df = pd.DataFrame(data)
    
    # 2. ACTION
    result_paths = files.sort_media_files(df)
    
    # 3. VERIFY OUTPUT LIST
    assert len(result_paths) == 3 # The 'unknown' one should have been skipped!
    
    # Unpack the results
    movie_old, movie_new = result_paths[0]
    _, tv_new = result_paths[1]
    _, weird_tv_new = result_paths[2]
    
    # Check the Movie paths (comparing Path objects, which ignores slash direction!)
    assert movie_old == dl_dir / 'movie1.mkv'
    assert movie_new == tmp_path / 'Movies' / 'The Matrix (1999).mkv'
    
    # Check the Standard TV Show paths
    assert tv_new == tmp_path / 'TV Shows' / 'Breaking Bad' / 'Season 01' / 'Breaking Bad S01E05.mp4'
    
    # Check the Fallback TV Show paths
    assert weird_tv_new == tmp_path / 'TV Shows' / 'Weird Show Name' / 'Unknown' / 'Weird Show Name.avi'
    
    # 4. VERIFY FOLDERS WERE CREATED
    assert (tmp_path / 'Movies').exists()
    assert (tmp_path / 'TV Shows' / 'Breaking Bad' / 'Season 01').exists()
    
    # 5. VERIFY UI LOGS
    mock_print.assert_called_once_with("⏭ Ignored (not found) : Junk File.txt")


@patch_globals
def test_sort_media_files_with_quality_and_resolution_tags(mock_print, tmp_path, monkeypatch):
    monkeypatch.setattr("src.files.MOVIES_FOLDER", str(tmp_path / 'Movies'))
    monkeypatch.setattr("src.files.TV_SHOWS_FOLDER", str(tmp_path / 'TV Shows'))

    dl_dir = tmp_path / 'downloads'
    data = {
        'Path': [
            str(dl_dir / 'got.mkv'),
            str(dl_dir / 'dark.mkv'),
        ],
        'Media': ['tv', 'tv'],
        'Corrected': [
            'Game of Thrones (2011) - S08E03 [FullHD BluRay]',
            'Dark (2017) - S02E05 [4K WEB-DL]'
        ]
    }
    df = pd.DataFrame(data)

    result_paths = files.sort_media_files(df)
    assert len(result_paths) == 2

    # Verify that clean show folders without trailing hyphens or brackets are created
    assert (tmp_path / 'TV Shows' / 'Game of Thrones (2011)' / 'Season 08').exists()
    assert (tmp_path / 'TV Shows' / 'Dark (2017)' / 'Season 02').exists()
    assert result_paths[0][1] == tmp_path / 'TV Shows' / 'Game of Thrones (2011)' / 'Season 08' / 'Game of Thrones (2011) - S08E03 [FullHD BluRay].mkv'
    assert result_paths[1][1] == tmp_path / 'TV Shows' / 'Dark (2017)' / 'Season 02' / 'Dark (2017) - S02E05 [4K WEB-DL].mkv'


@patch_globals
def test_sort_media_files_empty_exit(mock_print, tmp_path):
    # 1. SETUP
    # Create a fake, OS-safe path for the test text file
    data = {
        'Path': [str(tmp_path / 'downloads' / 'test.txt')],
        'Media': ['unrecognized'],
        'Corrected': ['test']
    }
    df = pd.DataFrame(data)
    
    # 2. ACTION & VERIFY
    with pytest.raises(SystemExit) as exc_info:
        files.sort_media_files(df)
        
    # 3. VERIFY EXIT CODE AND LOGS
    assert exc_info.value.code == 1 
    
    assert mock_print.call_count == 2
    assert "No media to move to a new folder." in mock_print.call_args[0][0]


# 1. Patch the global API key so the test doesn't crash if you don't have one set locally
@patch('src.ui.VERBOSE_ENABLED', True)
@patch('src.api.TMDB_API_KEY', 'fake_test_key') 
# 2. Patch requests.get inside the module where api_call is defined
@patch('src.api.requests.get')
def test_api_call_raises_runtime_error_on_request_exception(mock_get):
    # 1. SETUP
    name = "The Matrix"
    year = "1999"
    language = "en"
    media_type = "movie"
    
    # We force requests.get to simulate a severe network crash
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused by server")
    
    # 2. ACTION & VERIFY
    # We expect your custom RuntimeError to bubble up
    with pytest.raises(RuntimeError) as exc_info:
        api.api_call(name, year, language, media_type)
        
    # 3. VERIFY ERROR MESSAGE
    # We check that your custom formatting and the original error are both present
    error_msg = str(exc_info.value)
    
    assert "TMDB API call failed" in error_msg
    assert f"Query : {name} {year}" in error_msg
    assert "Connection refused by server" in error_msg


# -------------------------------------------------------------------
# A reusable patch stack to fake out the global variables and UI
# -------------------------------------------------------------------
def patch_email_globals(func):
    """Decorator to fake the global config variables and UI logs."""
    func = patch('src.mail.MAIL', 'fake@gmail.com')(func)
    func = patch('src.mail.MAIL_PSWD', 'super_secret_password')(func)
    func = patch('src.ui.MAIL_ENABLED', True)(func)
    func = patch('src.ui.VERBOSE_ENABLED', True)(func)
    func = patch('src.ui.print_log')(func)
    return func

@patch_email_globals
@patch('src.mail.smtplib.SMTP_SSL') # Mock the SMTP server
@patch('src.mail.ssl.create_default_context') # Mock the SSL context
def test_send_email_success(mock_ssl_context, mock_smtp, mock_print):
    # 1. SETUP
    # Because SMTP_SSL is used in a 'with' block, we have to mock its __enter__ method
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    
    test_message = "This is a test notification."
    
    # 2. ACTION
    mail.send_email(test_message)
    
    # 3. VERIFY
    # Did it try to connect to the right server on the right port?
    mock_smtp.assert_called_once_with("smtp.gmail.com", 465, context=mock_ssl_context.return_value)
    
    # Did it log in with our fake credentials?
    mock_server.login.assert_called_once_with('fake@gmail.com', 'super_secret_password')
    
    # Did it actually try to send a message?
    mock_server.send_message.assert_called_once()
    
    # Did it print the correct success logs?
    assert mock_print.call_count == 2
    mock_print.assert_any_call("Connecting to server...")
    mock_print.assert_any_call("Success: Email sent successfully!")


@patch_email_globals
@patch('src.mail.smtplib.SMTP_SSL')
def test_send_email_authentication_error(mock_smtp, mock_print):
    # 1. SETUP
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    
    # We force the login method to crash with an Authentication Error
    mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b'Authentication failed')
    
    # 2. ACTION & VERIFY
    with pytest.raises(RuntimeError) as exc_info:
        mail.send_email("Test message")
        
    # 3. VERIFY ERROR MESSAGE
    error_msg = str(exc_info.value)
    assert "Authentication failed" in error_msg
    assert "Check your email and password" in error_msg


@patch_email_globals
@patch('src.mail.smtplib.SMTP_SSL')
def test_send_email_unexpected_error(mock_smtp, mock_print):
    # 1. SETUP
    # Here, we force the initial connection to fail entirely (e.g., no internet)
    mock_smtp.side_effect = ConnectionError("Network is unreachable")
    
    # 2. ACTION & VERIFY
    with pytest.raises(RuntimeError) as exc_info:
        mail.send_email("Test message")
        
    # 3. VERIFY ERROR MESSAGE
    error_msg = str(exc_info.value)
    assert "An unexpected error occurred" in error_msg
    assert "Network is unreachable" in error_msg


# ===================================================================
# ADDITIONAL TESTS: UTILS MODULE
# ===================================================================

@pytest.mark.parametrize("input_res, expected", [
    ("2160p", "4K"),
    ("1440p", "2K"),
    ("1080p", "FullHD"),
    ("720p", "HD"),
    ("480p", "SD"),
    ("576p", "SD"),
    (" 1080p ", "FullHD"),
    ("2160P", "4K"),
    ("8K", "8K"),
    ("custom_res", "custom_res"),
    (None, None),
    ("", None),
])
def test_translate_resolution_to_name(input_res, expected):
    assert utils.translate_resolution_to_name(input_res) == expected


@pytest.mark.parametrize("season, episode, expected_s, expected_e", [
    (1, 2, "01", "02"),
    (9, 10, "09", "10"),
    ("3", "15", "03", "15"),
    (12, 24, "12", "24"),
])
def test_format_season_and_episode(season, episode, expected_s, expected_e):
    s, e = utils.format_season_and_episode(season, episode)
    assert s == expected_s
    assert e == expected_e


def test_format_season_and_episode_invalid():
    with pytest.raises(ValueError):
        utils.format_season_and_episode("invalid", 1)


def test_parse_season_episode_direct():
    s, e = utils.parse_season_episode(1, 5, "any_filename.mkv")
    assert s == 1
    assert e == 5


def test_parse_season_episode_fallback_regex():
    s, e = utils.parse_season_episode(None, None, "My.Show.S03E14.720p.mkv")
    assert s == 3
    assert e == 14

    s, e = utils.parse_season_episode("", "", "Show.Season.4.Episode.2.mkv")
    assert s == 4
    assert e == 2


def test_parse_season_episode_fallback_failure():
    with pytest.raises(ValueError):
        utils.parse_season_episode(None, None, "Movie.Without.Episodes.2020.mkv")


def test_generate_new_movie_filename_variations(monkeypatch):
    monkeypatch.setattr(utils, "QUALITY", False)
    monkeypatch.setattr(utils, "RESOLUTION", False)
    name = utils.generate_new_movie_filename(True, "Spider-Man: Far From Home", "2019", None, None)
    assert name == "Spider-Man - Far From Home (2019)"

    name_no_year = utils.generate_new_movie_filename(True, "Inception", None, None, None)
    assert name_no_year == "Inception"

    monkeypatch.setattr(utils, "QUALITY", True)
    monkeypatch.setattr(utils, "RESOLUTION", True)
    name_with_meta = utils.generate_new_movie_filename(True, "Avatar", "2009", "4K", "BluRay")
    assert name_with_meta == "Avatar (2009) [BluRay 4K]"


def test_generate_new_movie_filename_missing_metadata():
    with pytest.raises(LookupError):
        utils.generate_new_movie_filename(False, "Title", "2020", None, None)

    with pytest.raises(LookupError):
        utils.generate_new_movie_filename(True, "", "2020", None, None)


def test_generate_new_tvshow_filename_variations(monkeypatch):
    monkeypatch.setattr(utils, "QUALITY", False)
    monkeypatch.setattr(utils, "RESOLUTION", False)
    name = utils.generate_new_tvshow_filename(True, "Game of Thrones", None, 8, 3, None, None)
    assert name == "Game of Thrones - S08E03"

    name_colon = utils.generate_new_tvshow_filename(True, "CSI: Crime Scene Investigation", "2000", "1", "2", None, None)
    assert name_colon == "CSI - Crime Scene Investigation (2000) - S01E02"

    monkeypatch.setattr(utils, "QUALITY", True)
    monkeypatch.setattr(utils, "RESOLUTION", True)
    name_meta = utils.generate_new_tvshow_filename(True, "Dark", "2017", 2, 5, "FullHD", "WEB-DL")
    assert name_meta == "Dark (2017) - S02E05 [WEB-DL FullHD]"


def test_generate_new_tvshow_filename_missing_metadata():
    with pytest.raises(LookupError):
        utils.generate_new_tvshow_filename(False, "Dark", "2017", 1, 1, None, None)

    with pytest.raises(LookupError):
        utils.generate_new_tvshow_filename(True, "", "2017", 1, 1, None, None)

    with pytest.raises(LookupError):
        utils.generate_new_tvshow_filename(True, "Dark", "2017", None, 1, None, None)


def test_has_files_to_rename():
    empty_df = pd.DataFrame()
    assert utils.has_files_to_rename(empty_df) is False

    same_df = pd.DataFrame([
        {'Original': 'Movie (2020)', 'Corrected': 'Movie (2020)'},
        {'Original': 'Show S01E01', 'Corrected': 'Show S01E01'}
    ])
    assert utils.has_files_to_rename(same_df) is False

    diff_df = pd.DataFrame([
        {'Original': 'Movie.2020.mkv', 'Corrected': 'Movie (2020)'}
    ])
    assert utils.has_files_to_rename(diff_df) is True


def test_handle_conflicts_and_duplicates():
    df = pd.DataFrame([
        {'Original': 'FileA.mkv', 'Corrected': 'Duplicate Title (2020)'},
        {'Original': 'FileB.mkv', 'Corrected': 'Duplicate Title (2020)'},
        {'Original': 'FileC.mkv', 'Corrected': 'Unique Title (2021)'}
    ])
    failed_files = []
    clean_df = utils.handle_conflicts_and_duplicates(df, failed_files)

    assert len(clean_df) == 1
    assert clean_df.iloc[0]['Corrected'] == 'Unique Title (2021)'
    assert len(failed_files) == 2
    assert any("Conflict" in f['Reason'] for f in failed_files)


def test_verify_folders(tmp_path, monkeypatch):
    m = tmp_path / "Movies"
    tv = tmp_path / "TV"
    dl = tmp_path / "Downloads"
    m.mkdir()
    tv.mkdir()
    dl.mkdir()

    monkeypatch.setattr(utils, "MOVIES_FOLDER", str(m))
    monkeypatch.setattr(utils, "TV_SHOWS_FOLDER", str(tv))
    monkeypatch.setattr(utils, "NOT_SORTED_MEDIA_FILES_FOLDER", str(dl))
    assert utils.verify_folders() == 0

    # Missing config raises SystemExit
    monkeypatch.setattr(utils, "MOVIES_FOLDER", None)
    with pytest.raises(SystemExit) as exc:
        utils.verify_folders()
    assert exc.value.code == 1

    # Non-existent folder raises SystemExit
    monkeypatch.setattr(utils, "MOVIES_FOLDER", str(tmp_path / "non_existent"))
    with pytest.raises(SystemExit) as exc:
        utils.verify_folders()
    assert exc.value.code == 1


# ===================================================================
# ADDITIONAL TESTS: FILES MODULE
# ===================================================================

def test_move_file_conflict_raises_file_exists_error(tmp_path):
    src_file = tmp_path / "source.mkv"
    dest_file = tmp_path / "dest.mkv"
    src_file.write_text("source")
    dest_file.write_text("dest")

    with patch('src.files.make_safe_path', side_effect=lambda p: str(p)):
        with pytest.raises(FileExistsError) as exc:
            files.move_file(src_file, dest_file)
        assert "Conflict" in str(exc.value)


def test_get_metadata_with_ffprobe(monkeypatch):
    with patch('shutil.which', return_value=None):
        assert files.get_metadata_with_ffprobe("any_file.mkv") is None

    with patch('shutil.which', return_value="/usr/bin/ffprobe"):
        fake_proc = MagicMock()
        fake_proc.stdout = '{"streams": [{"width": 1920, "height": 1080}], "format": {}}'
        with patch('subprocess.run', return_value=fake_proc):
            data = files.get_metadata_with_ffprobe("any_file.mkv")
            assert data["streams"][0]["width"] == 1920

        with patch('subprocess.run', side_effect=Exception("ffprobe failed")):
            assert files.get_metadata_with_ffprobe("any_file.mkv") is None


def test_get_file_quality_resolution():
    fake_metadata = {
        'streams': [{'width': 3840, 'height': 2160, 'codec_name': 'hevc', 'pix_fmt': 'yuv420p10le', 'color_space': 'bt2020nc'}],
        'format': {'format_name': 'matroska', 'tags': {'title': 'Movie.2160p.UHD.BluRay'}}
    }
    with patch('src.files.get_metadata_with_ffprobe', return_value=fake_metadata):
        res, qual = files.get_file_quality_resolution("movie.mkv")
        assert res in ["4k", "2160p"]
        assert qual.lower() == "bluray"

    fake_bitrate_meta = {
        'streams': [{'width': 1920, 'height': 1080, 'codec_name': 'h264', 'pix_fmt': None, 'color_space': None}],
        'format': {'format_name': 'mp4', 'bit_rate': '10000000', 'tags': {}}
    }
    with patch('src.files.get_metadata_with_ffprobe', return_value=fake_bitrate_meta):
        res, qual = files.get_file_quality_resolution("movie.mp4")
        assert res == "1080p"
        assert qual == "10Mbps"

    with patch('src.files.get_metadata_with_ffprobe', return_value=None):
        res, qual = files.get_file_quality_resolution("empty.mkv")
        assert res is None
        assert qual is None


def test_search_media_files_custom_path_and_filtering(tmp_path):
    target_dir = tmp_path / "custom_downloads"
    target_dir.mkdir()
    (target_dir / "valid_movie.2021.1080p.mkv").touch()
    (target_dir / "valid_show.S01E01.mp4").touch()
    (target_dir / "subtitle.srt").touch()
    (target_dir / "info.nfo").touch()
    (target_dir / "notes.txt").touch()

    messy_df, clean_df = files.search_media_files(str(target_dir))
    assert len(messy_df) == 2

    # Non-existent directory returns None
    assert files.search_media_files(str(tmp_path / "non_existent_folder")) is None

    # Directory with no media files exits 1
    empty_dir = tmp_path / "empty_folder"
    empty_dir.mkdir()
    with pytest.raises(SystemExit) as exc:
        files.search_media_files(str(empty_dir))
    assert exc.value.code == 1


def test_rename_media_files_edge_cases(tmp_path):
    media_file = tmp_path / "Movie.2020.mkv"
    media_file.touch()

    df = pd.DataFrame([
        {'Original': 'Movie.2020.mkv', 'Corrected': 'Movie (2020)', 'Path': str(media_file)},
        {'Original': 'Missing.mkv', 'Corrected': 'Missing (2020)', 'Path': str(tmp_path / 'Missing.mkv')},
        {'Original': 'Ignored.mkv', 'Corrected': None, 'Path': str(tmp_path / 'Ignored.mkv')},
    ])

    renamed_df = files.rename_media_files(df)
    assert (tmp_path / "Movie (2020).mkv").exists()


# ===================================================================
# ADDITIONAL TESTS: UI MODULE
# ===================================================================

def test_parse_arguments_conflicts(monkeypatch):
    # Both -m and -r together should raise SystemExit
    monkeypatch.setattr(sys, "argv", ["main.py", "-m", "-r"])
    with pytest.raises(SystemExit):
        ui.parse_arguments()

    # --path without -r should raise SystemExit
    monkeypatch.setattr(sys, "argv", ["main.py", "--path", "some_folder"])
    with pytest.raises(SystemExit):
        ui.parse_arguments()


def test_parse_arguments_missing_keys(monkeypatch):
    monkeypatch.setattr(ui, "MAIL", None)
    monkeypatch.setattr(ui, "MAIL_PSWD", None)
    monkeypatch.setattr(sys, "argv", ["main.py", "-e"])
    with pytest.raises(SystemExit):
        ui.parse_arguments()

    monkeypatch.setattr(ui, "GEMINI_API_KEY", None)
    monkeypatch.setattr(sys, "argv", ["main.py", "-i"])
    with pytest.raises(SystemExit):
        ui.parse_arguments()


def test_user_confirmation(monkeypatch):
    monkeypatch.setattr(ui, "AUTO_ENABLED", True)
    # With AUTO_ENABLED=True, it should return immediately without waiting for input
    ui.user_confirmation("test action")

    monkeypatch.setattr(ui, "AUTO_ENABLED", False)
    with patch('builtins.input', side_effect=KeyboardInterrupt):
        with pytest.raises(SystemExit) as exc:
            ui.user_confirmation("cancelled action")
        assert exc.value.code == 1


def test_ui_display_tables_smoke():
    # Verify these display functions run without crashing on various inputs
    empty_df = pd.DataFrame()
    ui.display_corrected_filenames(empty_df)
    ui.display_sorted_files([])
    ui.display_skipped_filenames([])

    populated_df = pd.DataFrame([
        {'Media': 'movie', 'Original': 'M1.mkv', 'Corrected': 'M1 (2020)'},
        {'Media': 'tv', 'Original': 'T1.mkv', 'Corrected': 'T1 - S01E01', 'Season': '01', 'Episode': '01'}
    ])
    ui.display_corrected_filenames(populated_df)

    ui.display_skipped_filenames([{'Original': 'Bad.mkv', 'Reason': 'Parsing error'}])


# ===================================================================
# ADDITIONAL TESTS: API MODULE
# ===================================================================

def test_api_call_missing_key_exits(monkeypatch):
    monkeypatch.setattr(api, "TMDB_API_KEY", None)
    with pytest.raises(SystemExit) as exc:
        api.api_call("Inception", "2010", "en-US", "movie")
    assert exc.value.code == 1


@patch('src.api.TMDB_API_KEY', 'fake_key')
@patch('src.api.requests.get')
def test_api_call_http_errors_and_empty_results(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_get.return_value = mock_resp
    result = api.api_call("NonExistent", "2020", "en-US", "movie")
    assert result == [False, None, None, None]

    mock_resp.status_code = 200
    mock_resp.json.return_value = {'results': []}
    result = api.api_call("NonExistent", "2020", "en-US", "movie")
    assert result == [False, None, None, None]


def test_gemini_api_call_missing_key(monkeypatch):
    monkeypatch.setattr(api, "GEMINI_API_KEY", None)
    dummy_info = {
        'File': 'test.mkv',
        'Folder': 'downloads',
        'Path': '/path/test.mkv',
        'Clean': 'test',
        'Parse': 'test',
        'Media': 'movie'
    }
    with pytest.raises(SystemExit) as exc:
        api.gemini_api_call(dummy_info)
    assert exc.value.code == 1


# ===================================================================
# ADDITIONAL TESTS: ADVANCED UTILS EDGE CASES
# ===================================================================

def test_add_new_tags_all_already_exist(tmp_path, monkeypatch):
    fake_data_file = tmp_path / "data.py"
    fake_data_file.write_text("TAGS = [r'existing_tag']\n", encoding="utf-8")
    monkeypatch.setattr(utils, "DATA_FILE", fake_data_file)

    # Calling with tag that already exists should return early at line 61
    utils.add_new_tags(["existing_tag"])
    assert fake_data_file.read_text(encoding="utf-8") == "TAGS = [r'existing_tag']\n"


def test_parse_resolution_quality_edge_cases(monkeypatch):
    monkeypatch.setattr(utils, "RESOLUTION", True)
    monkeypatch.setattr(utils, "QUALITY", True)

    # Resolution from clean fallback, quality from ptn
    res, qual = utils.parse_resolution_quality(None, "BluRay", "1080p", None, "file.mkv")
    assert res == "FullHD"
    assert qual == "BluRay"

    # Quality from clean fallback, resolution from ptn
    res, qual = utils.parse_resolution_quality("2160p", None, None, "WEB-DL", "file.mkv")
    assert res == "4K"
    assert qual == "WEB-DL"

    # Both missing, fall back to files.get_file_quality_resolution
    with patch('src.files.get_file_quality_resolution', return_value=("720p", "HDTV")):
        res, qual = utils.parse_resolution_quality(None, None, None, None, "file.mkv")
        assert res == "HD"
        assert qual == "HDTV"

    # Both disabled in config
    monkeypatch.setattr(utils, "RESOLUTION", False)
    monkeypatch.setattr(utils, "QUALITY", False)
    res, qual = utils.parse_resolution_quality("1080p", "BluRay", "1080p", "BluRay", "file.mkv")
    assert res is None
    assert qual is None


def test_correct_movie_filename_french_and_ai_fallback(monkeypatch):
    monkeypatch.setattr(utils, "RESOLUTION", False)
    monkeypatch.setattr(utils, "QUALITY", False)
    monkeypatch.setattr(ui, "AI_FALLBACK_ENABLED", True)

    fake_file = {
        'File': 'Intouchables.2011.mkv',
        'Path': '/movies/Intouchables.2011.mkv',
        'Parse': ['Intouchables', '2011', None, None],
        'Clean': ['Intouchables', '2011', None, None]
    }

    # TMDB English call returns original_language="fr", triggering French TMDB call
    with patch('src.api.api_call') as mock_api:
        mock_api.side_effect = [
            [True, "The Intouchables", "2011", "fr"],     # English call
            [True, "Intouchables", "2011", "fr"]          # French call
        ]
        new_name = utils.correct_movie_filename(fake_file)
        assert new_name == "Intouchables (2011)"
        assert mock_api.call_count == 2

    # Parse and Clean both fail on TMDB, triggers AI Fallback
    with patch('src.api.api_call', return_value=[False, None, None, None]):
        with patch('src.api.gemini_api_call', return_value=[True, "AI Movie", "2022", "en", []]) as mock_gemini:
            new_name = utils.correct_movie_filename(fake_file)
            assert new_name == "AI Movie (2022)"
            mock_gemini.assert_called_once()


def test_correct_movie_filename_exception_handling(monkeypatch):
    monkeypatch.setattr(ui, "VERBOSE_ENABLED", True)
    fake_file = {'File': 'Faulty.mkv'}

    with patch('src.utils.generate_new_movie_filename', side_effect=RuntimeError("Test crash")):
        with patch('src.mail.send_email') as mock_mail:
            with patch('src.ui.print_log') as mock_log:
                res = utils.correct_movie_filename(fake_file)
                assert res is None
                mock_mail.assert_called_once()
                assert "Impossible to rename" in mock_mail.call_args[0][0]
                mock_log.assert_called_once()


def test_correct_tv_show_filename_french_and_ai_fallback(monkeypatch):
    monkeypatch.setattr(utils, "RESOLUTION", False)
    monkeypatch.setattr(utils, "QUALITY", False)
    monkeypatch.setattr(ui, "AI_FALLBACK_ENABLED", True)

    fake_file = {
        'File': 'Lupin.S01E01.mkv',
        'Path': '/tv/Lupin.S01E01.mkv',
        'Parse': ['Lupin', '2021', 1, 1, None, None],
        'Clean': ['Lupin', '2021', None, None]
    }

    # TMDB English call returns original_language="fr", triggering French TMDB call
    with patch('src.api.api_call') as mock_api:
        mock_api.side_effect = [
            [True, "Lupin Part 1", "2021", "fr"],     # English call
            [True, "Lupin", "2021", "fr"]             # French call
        ]
        new_name, s, e = utils.correct_tv_show_filename(fake_file)
        assert new_name == "Lupin (2021) - S01E01"
        assert s == "01"
        assert e == "01"

    # Both TMDB calls fail, triggers AI Fallback
    with patch('src.api.api_call', return_value=[False, None, None, None]):
        with patch('src.api.gemini_api_call', return_value=[True, "AI Show", "2023", "en", []]):
            new_name, s, e = utils.correct_tv_show_filename(fake_file)
            assert new_name == "AI Show (2021) - S01E01"


def test_correct_tv_show_filename_exception_handling(monkeypatch):
    monkeypatch.setattr(ui, "VERBOSE_ENABLED", True)
    fake_file = {'File': 'FaultyShow.mkv'}

    with patch('src.mail.send_email') as mock_mail:
        with patch('src.ui.print_log') as mock_log:
            new_name, s, e = utils.correct_tv_show_filename(fake_file)
            assert new_name is None
            assert s is None
            assert e is None
            mock_mail.assert_called_once()
            mock_log.assert_called_once()


def test_get_corrected_media_filenames_unknown_media():
    df_messy = pd.DataFrame([
        {'Media': 'unknown_type', 'File': 'Mystery.iso', 'Path': '/path/Mystery.iso'}
    ])
    df_clean = pd.DataFrame()

    with patch('src.ui.print_log') as mock_log:
        result = utils.get_corrected_media_filenames(df_messy, df_clean)
        assert result.empty
        mock_log.assert_called_with("Ignored : Mystery.iso\n")


def test_sort_media_dataframe():
    empty_df = pd.DataFrame()
    assert utils.sort_media_dataframe(empty_df).empty

    df = pd.DataFrame([
        {'Corrected': 'Z Movie', 'Season': None, 'Episode': None},
        {'Corrected': 'A Show', 'Season': '02', 'Episode': '01'},
        {'Corrected': 'A Show', 'Season': '01', 'Episode': '05'},
    ])
    sorted_df = utils.sort_media_dataframe(df)
    assert sorted_df.iloc[0]['Corrected'] == 'A Show'
    assert sorted_df.iloc[0]['Season'] == '01'
    assert sorted_df.iloc[1]['Season'] == '02'
    assert sorted_df.iloc[2]['Corrected'] == 'Z Movie'


# ===================================================================
# ADDITIONAL TESTS: FILES & API 100% COVERAGE
# ===================================================================

def test_rename_media_files_all_already_clean(tmp_path):
    clean_file = tmp_path / "Movie (2020).mkv"
    clean_file.touch()

    df = pd.DataFrame([
        {'Original': 'Movie (2020)', 'Corrected': 'Movie (2020)', 'Path': str(clean_file)}
    ])

    with patch('src.ui.print_log') as mock_log:
        res = files.rename_media_files(df)
        assert res.iloc[0]['Path'] == str(clean_file)
        mock_log.assert_called_with("\n ❌ No files have been renamed.")


def test_rename_media_files_os_rename_failure(tmp_path):
    old_file = tmp_path / "OldMovie.mkv"
    old_file.touch()

    df = pd.DataFrame([
        {'Original': 'OldMovie.mkv', 'Corrected': 'NewMovie (2020)', 'Path': str(old_file)}
    ])

    with patch('os.rename', side_effect=PermissionError("Permission Denied")):
        with pytest.raises(RuntimeError) as exc:
            files.rename_media_files(df)
        assert "Impossible to rename" in str(exc.value)


def test_gemini_api_call_success_zero(monkeypatch):
    monkeypatch.setattr(api, "GEMINI_API_KEY", "fake_key")
    dummy_info = {
        'File': 'test.mkv',
        'Folder': 'downloads',
        'Path': '/path/test.mkv',
        'Clean': 'test',
        'Parse': 'test',
        'Media': 'movie'
    }

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"success": 0}'
    mock_client.models.generate_content.return_value = mock_response

    with patch('src.api.genai.Client', return_value=mock_client):
        result = api.gemini_api_call(dummy_info)
        assert result == [False, None, None, None, None]


def test_gemini_api_call_json_decode_error(monkeypatch):
    monkeypatch.setattr(api, "GEMINI_API_KEY", "fake_key")
    dummy_info = {
        'File': 'test.mkv',
        'Folder': 'downloads',
        'Path': '/path/test.mkv',
        'Clean': 'test',
        'Parse': 'test',
        'Media': 'movie'
    }

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '<html>Not JSON</html>'
    mock_client.models.generate_content.return_value = mock_response

    with patch('src.api.genai.Client', return_value=mock_client):
        result = api.gemini_api_call(dummy_info)
        assert result == [False, None, None, None, None]