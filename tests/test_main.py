import os
import sys
import shutil
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch
from src import ui, files, utils, api

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
    "A Knight of the Seven Kingdoms S01E01.mkv",
    "Suits S01E01.mkv"
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
    "Breaking Bad S01E01",
    "Game of Thrones S08E03",
    "Stranger Things S04E01",
    "The Boys S03E06",
    "True Detective S01E04",
    "Mad Max - Fury Road (2015)",
    "Blade Runner 2049 (2017)",
    "Jurassic Park (1993)",
    "The Godfather (1972)",
    "Parasite (2019)",
    "Everything Everywhere All at Once (2022)",
    "Arcane S01E01",
    "The Last of Us S01E01",
    "Titanic (1997)",
    "Alien (1979)"
]

donnees_test_api = [
    ("Blade Runner 2049", 2017, "movie", ["Blade Runner 2049", "2017", "en"]),
    ("Inception", 2010, "movie", ["Inception", "2010", "en"]),
    ("Parasite", 2019, "movie", ["Parasite", "2019", "ko"]),
    ("The Matrix", None, "movie", ["The Matrix", "1999", "en"]),
    ("Spirited Away", 2001, "movie", ["Spirited Away", "2001", "ja"]),
    ("Stranger Things", None, "tv", ["Stranger Things", "unkn", "en"]),
    ("Breaking Bad", 2008, "tv", ["Breaking Bad", "unkn", "en"]),
    ("Game of Thrones", None, "tv", ["Game of Thrones", "unkn", "en"]),
    ("Dark", 2017, "tv", ["Dark", "unkn", "de"]),
    ("Lupin", None, "tv", ["Lupin", "unkn", "fr"]),
]

MOVIES_FOLDER_NAME = "Films"
TV_SHOWS_FOLDER_NAME = "Séries"
NOT_SORTED_MEDIA_FILES_FOLDER_NAME = ".download"

@pytest.fixture
def setup(monkeypatch, tmp_path):
    dossier_download = tmp_path / NOT_SORTED_MEDIA_FILES_FOLDER_NAME
    dossier_download.mkdir()
    (tmp_path / MOVIES_FOLDER_NAME).mkdir()
    (tmp_path / TV_SHOWS_FOLDER_NAME).mkdir()
    
    monkeypatch.setattr("src.utils.PATH", str(tmp_path))
    monkeypatch.setattr("src.files.PATH", str(tmp_path))
    
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

def test_path_verification_with_correct_env(setup):
    result = utils.verify_path()
    assert result == 0

def test_path_verification_1_must_exit_with_one(monkeypatch, tmp_path):
    (tmp_path / NOT_SORTED_MEDIA_FILES_FOLDER_NAME).mkdir()
    (tmp_path / f"{MOVIES_FOLDER_NAME}s").mkdir() # Faux nom exprès
    (tmp_path / TV_SHOWS_FOLDER_NAME).mkdir()

    monkeypatch.setattr("src.utils.PATH", str(tmp_path))

    with pytest.raises(SystemExit) as e:
        utils.verify_path()
        
    assert e.value.code == 1

def test_path_verification_2_must_exit_with_one(monkeypatch, tmp_path):
    (tmp_path / NOT_SORTED_MEDIA_FILES_FOLDER_NAME).mkdir()
    (tmp_path / MOVIES_FOLDER_NAME).mkdir()
    (tmp_path / TV_SHOWS_FOLDER_NAME).mkdir()
    (tmp_path / "Error").mkdir() # wrong folder

    monkeypatch.setattr("src.utils.PATH", str(tmp_path))

    with pytest.raises(SystemExit) as e:
        utils.verify_path()
        
    assert e.value.code == 1

def test_path_verification_3_must_exit_with_one(monkeypatch, tmp_path):
    (tmp_path / NOT_SORTED_MEDIA_FILES_FOLDER_NAME).mkdir()
    (tmp_path / MOVIES_FOLDER_NAME).mkdir() # missing folder

    monkeypatch.setattr("src.utils.PATH", str(tmp_path))

    with pytest.raises(SystemExit) as e:
        utils.verify_path()
        
    assert e.value.code == 1

def test_search_media_files(setup):
    media_files = files.search_media_files()
    assert len(media_files) == 30
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
    assert api.api_call(name, year, "en-US", media_type) == [None, None, None]

def test_get_corrected_media_filenames(setup):
    media_files = files.search_media_files()
    corrected_filenames = utils.get_corrected_media_filenames(media_files)
    for index,movie in corrected_filenames.iterrows():
        i = 0
        found = False
        while (i<len(fichiers_corriges)-1 and not found):
            if corrected_filenames.loc[index,'Original'] == fichiers[i]:
                assert movie['Corrected'] == fichiers_corriges[i]
                found = True
            i=i+1

def test_rename_media_files(setup):
    media_files = files.search_media_files()
    corrected_filenames = files.get_corrected_media_filenames(media_files)
    files.rename_media_files(corrected_filenames)

    # scan of the folder with corrected filenames
    target_dir = Path(NOT_SORTED_MEDIA_FILES_FOLDER_NAME)
    for file_path in target_dir.rglob('*'):
        corrected_name = file_path.stem.strip()
        if corrected_name not in ["Arrival (2016)", "A Knight of the Seven Kingdoms S01E01", "Suits S01E01"] :
            assert corrected_name in fichiers_corriges

# Test Group 1: Valid Arguments
@pytest.mark.parametrize("mock_args, expected_result", [
    # --- Cas classiques ---
    (["main.py"], 0),             # Aucun argument -> "auto" par défaut
    (["main.py", "auto"], 0),     # Mode explicite "auto" -> "auto"
    (["main.py", "manual"], 0), # Mode explicite "manual" -> "manual"
    
    # --- Nouveaux cas avec "log" ---
    (["main.py", "log"], 0),               # Juste "log" -> mode "auto" par défaut
    (["main.py", "auto", "log"], 0),       # "auto" + "log" -> "auto"
    (["main.py", "log", "auto"], 0),       # L'ordre ne doit pas importer
    (["main.py", "manual", "log"], 0),   # "manual" + "log" -> "manual"
    (["main.py", "log", "manual"], 0),   # L'ordre ne doit pas importer
])
def test_verify_arguments_valid(mock_args, expected_result):
    # patch.object remplace temporairement sys.argv par mock_args
    with patch.object(sys, 'argv', mock_args):
        result = utils.verify_arguments()
        assert result == expected_result

# Test Group 2: Invalid Arguments (Expect SystemExit)
@pytest.mark.parametrize("mock_args", [
    # --- Valeurs non reconnues ---
    (["main.py", "not a valid argument"]), # Mauvaise chaîne de caractères
    (["main.py", "random"]),               # Autre mauvaise chaîne
    (["main.py", "log", "random"]),        # Un bon et un mauvais argument
    
    # --- Incompatibilité ---
    (["main.py", "auto", "manual"]),       # Ne peut pas être "auto" et "manual" en même temps
    (["main.py", "manual", "auto"]),       # Pareil, peu importe l'ordre
    
    # --- Trop d'arguments (> 2) ---
    (["main.py", "manual", "log", "extra"]), # 3 arguments au lieu de 2 max
    (["main.py", "auto", "log", "manual"]),  # 3 arguments
])
def test_verify_arguments_invalid_exits(mock_args):
    with patch.object(sys, 'argv', mock_args):
        # On s'attend à ce que le programme appelle sys.exit(1)
        with pytest.raises(SystemExit) as excinfo:
            utils.verify_arguments()
        assert excinfo.value.code == 1

donnees_test_gemini_api = [(
    {
        'File': "Blade.Runner.2049.2017.2160p.UHD.BluRay.Remux.HEVC.HDR.TrueHD.7.1.Atmos.VOSTFR-TEAM.mkv",
        'Folder': NOT_SORTED_MEDIA_FILES_FOLDER_NAME,
        'Path': f"/home/ugo/movies/{NOT_SORTED_MEDIA_FILES_FOLDER_NAME}",
        'Clean': "Blade Runner 2049 2160p HEVC",
        'Parse': None,
        'Media': "movie"
    }, ["Blade Runner 2049", "2017", "en", ["2160p","HEVC"]])
]

@pytest.mark.parametrize("media_info, expected", donnees_test_gemini_api)
def test_gemini_api_call(media_info, expected):
    try:
        resultat = api.gemini_api_call(media_info)
        assert resultat == expected
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            pytest.skip("Skipped: Gemini API daily quota exceeded (429 RESOURCE_EXHAUSTED).")
        else:
            raise

donnees_wrong_test_gemini_api = [(
    {
        'File': "jkdvdqskldnvdsvsvsj.mkv",
        'Folder': NOT_SORTED_MEDIA_FILES_FOLDER_NAME,
        'Path': f"/home/ugo/movies/{NOT_SORTED_MEDIA_FILES_FOLDER_NAME}",
        'Clean': "zinovikns,dl",
        'Parse': None,
        'Media': "movie"
    }, [None, None, None, None])
]

@pytest.mark.parametrize("media_info, expected", donnees_wrong_test_gemini_api)
def test_error_gemini_api_call(media_info, expected):
    try:
        resultat = api.gemini_api_call(media_info)
        assert resultat == expected
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            pytest.skip("Skipped: Gemini API daily quota exceeded (429 RESOURCE_EXHAUSTED).")
        else:
            raise

def test_file_impossible_to_rename_and_mail():
    media_files = pd.DataFrame([{
        'File': "apjfpjkd.mkv",
        'Folder': NOT_SORTED_MEDIA_FILES_FOLDER_NAME,
        'Path': f"/home/ugo/movies/{NOT_SORTED_MEDIA_FILES_FOLDER_NAME}",
        'Clean': [None,None],
        'Parse': [None,None],
        'Media': "movie"
    }])
    
    try:
        corrected_filenames = files.get_corrected_media_filenames(media_files)
        assert corrected_filenames.iloc[0]['Corrected'] == "Not found"
        assert corrected_filenames.iloc[0]['Original'] == "apjfpjkd.mkv"
    except Exception as e:
        # check if the error is the Gemini 429 Quota Exceeded error
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            pytest.skip("Skipped: Gemini API daily quota exceeded (429 RESOURCE_EXHAUSTED).")
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
    ("Breaking.Bad.S01E01.Pilot.1080p.BluRay.x264.AC3.5.1.MULTI.VOSTFR-TV.mkv", "Breaking Bad Pilot", None), # S01E01 effacé, Pas d'année
    ("Game.of.Thrones.S08E03.1080p.AMZN.WEB-DL.DDP5.1.x264.VFF-GRP.mkv", "Game of Thrones", None),
    ("Stranger Things S04E01 2160p NF WEB-DL x265 10bit HDR DDP5.1 Atmos MULTI VF.mkv", "Stranger Things", None),
    ("The.Boys.S03E06.Herogasm.1080p.WEB.H264.EAC3.5.1.VOSTFR-RLS.mkv", "The Boys Herogasm", None),
    
    # --- 3. DÉJÀ PROPRES (Pour vérifier que la fonction ne casse rien) ---
    ("Arrival (2016).mkv", "Arrival", "2016"),
    ("A Knight of the Seven Kingdoms S01E01.mkv", "A Knight of the Seven Kingdoms", None), # S01E01 sera effacé par ta regex
    
    # Test de la suppression des URLs (http, https, www, .com, .fr, etc.)
    ("Super.Movie.2021.www.monsite.fr.1080p.mkv", "Super Movie", "2021"),
    ("Another.Film.https://torrent-site.com/movie.2018.mp4", "Another Film", "2018"),
    
    # Test de la suppression des nombres à 5 chiffres et plus (ex: IDs de torrents)
    ("Movie.With.Tracker.ID.1234567.2005.mkv", "Movie With Tracker ID", "2005"),
    ("Short.ID.98765.1998.avi", "Short ID", "1998"),
    
    # Test de formats d'années complexes ou multiples (ta fonction prend la 1ère occurrence)
    ("Movie.Set.In.2049.2017.1080p.mkv", "Movie Set In", "2049"),
    ("Year.In.Parentheses.(2023).mkv", "Year In Parentheses", "2023"),
    ("Trop___de...points---et_tirets.2010.mkv", "Trop de points et tirets", "2010"),
])
def test_clean_function(file_name, expected_title, expected_year):
    result_title, result_year = files.clean_filename(file_name)
    assert result_title == expected_title, f"Error on the title of the file: {file_name}"
    assert result_year == expected_year, f"Error on the year of the file: {file_name}"


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
    
    # Ne doit pas crasher, mais faire un print d'erreur
    utils.add_new_tags(["vostfr"])
    captured = capsys.readouterr()
    assert "Error : The fime" in captured.out
    
    # --- Cas d'erreur B : Le fichier existe mais n'a pas de liste TAGS ---
    invalid_file = tmp_path / "invalid_data.py"
    invalid_file.write_text("UNE_AUTRE_LISTE = ['a', 'b']", encoding="utf-8")
    monkeypatch.setattr(utils, "DATA_FILE", invalid_file)
    
    utils.add_new_tags(["vostfr"])
    captured = capsys.readouterr()
    assert "Impossible de localiser la liste TAGS" in captured.out
    
    # --- Cas d'erreur C : La liste fournie est vide ou None ---
    valid_file = tmp_path / "data.py"
    valid_file.write_text("TAGS = [r'1080p']", encoding="utf-8")
    monkeypatch.setattr(utils, "DATA_FILE", valid_file)
    
    # Ne doit rien faire du tout
    utils.add_new_tags([])
    utils.add_new_tags(None)
    
    # Le contenu doit être strictement identique
    assert valid_file.read_text(encoding="utf-8") == "TAGS = [r'1080p']"