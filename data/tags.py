TAGS = [
    # === RÉSOLUTIONS ===
    r'480p', r'720p', r'1080p', r'1080i', r'2160p', r'4k', r'8k', r'uhd',
    
    # === SOURCES (D'où vient la vidéo) ===
    r'bluray', r'bdrip', r'brrip', r'dvdrip', r'webrip', r'web\-dl', r'webdl', r'web', 
    r'hdrip', r'hdtv', r'pdtv', r'tvrip', r'cam', r'ts', r'telesync', r'remux', 
    
    # === CODECS VIDÉO & QUALITÉ ===
    r'x264', r'h264', r'avc', r'x265', r'h265', r'H\.265', r'hevc', r'av1', r'xvid', r'divx',
    r'10bit', r'12bit', r'sdr', r'hdr', r'hdr10', r'hdr10\+', r'dolby', r'vision', r'dv',
    r'hdlight', r'4klight', r'mhd', r'microhd', r'qtz', r'imax',
    
    # === AUDIO ===
    r'ac3', r'eac3', r'aac', r'dts(?:-?hd(?:\.?ma)?)?', r'dtshd', r'truehd', r'atmos', 
    r'flac', r'mp3', r'5\.1', r'7\.1', r'2\.0', r'3\.0', '5.1', '7.1', '2.0', r'dual', r'audio',
    r'MA\.5\.1', r'MA\.2\.0', r'MA\.7\.1', r'MA',
    
    # === LANGUES ET SOUS-TITRES ===
    r'vf', r'vff', r'vfq', r'vf2', r'vostfr-tag', r'truefrench', r'vostfr-tv', r'vostfr', r'vost', r'subfrench', 
    r'multi', r'fre', r'french', r'eng', r'english', r'vfi',
    
    # === VERSIONS & ÉDITIONS ===
    r'extended', r'unrated', r'director\.?s?\.?cut', r'dc', r'remastered', 
    r'repack', r'proper', r'limited', r'special', r'edition', r'uncut',

    # === Autres ===
    r'lihdl', r'fw', r'final', r'group', r'rls', r'dl', r'ddp5\.1', r'ddp51', r'team', r'ddp5', r'frg', r'grp', r'amzn', r'nf', r'DDLBase', r'EPSiLON', r'FraMeSToR', r'HYBRID', r'BYNDR', r'PmP', r'MMCK'
]

TLDS = [
    # === SAFE GENERIC TLDs (gTLDs) ===
    # Removed dangerous words like 'shop', 'club', 'site', 'space', 'name', 'click'
    r'com', r'net', r'org', r'info', r'biz', r'xyz', r'online', 
    r'vip', r'dev', r'icu', r'mobi', r'asia', r'aero', r'tech',
    
    # === ccTLDs : HIGH FREQUENCY / PIRACY / TRACKERS ===
    # Removed: 'to', 'is', 'me', 'eu', 'se', 'su', 'nu', 'la', 'ws'
    r'ru', r'sx', r'ch', r'cx', r'io', r'cc', 
    r'co', r'uk', r'nl', r'pw', r'vc', r'ag', r'bz', 
    r'ro', r'pe', r'ph', r'li', r'fm',

    # === ccTLDs : COUNTRIES AND TERRITORIES ===
    # Stripped of all English and French common words.
    # (Also missing: ts, tv, cd, bd, ma, nf, am due to video jargon conflicts)
    
    # A - B
    r'ac', r'ae', r'af', r'ai', r'al', r'ao', r'aq', r'ar', r'aw', r'ax', r'az',
    r'ba', r'bb', r'bf', r'bg', r'bh', r'bi', r'bj', r'bm', r'bn', r'bo', r'br', r'bs', r'bt', r'bv', r'bw', 
    
    # C - D
    r'ca', r'cf', r'cg', r'ck', r'cl', r'cm', r'cn', r'cr', r'cu', r'cv', r'cy', r'cz',
    r'dk', r'dm', r'dz',
    
    # E - F
    r'ec', r'ee', r'eg', r'er',
    r'fi', r'fj', r'fk', r'fo', r'fr', 
    
    # G - H
    r'ga', r'gb', r'gd', r'ge', r'gf', r'gg', r'gh', r'gi', r'gl', r'gm', r'gn', r'gp', r'gq', r'gr', r'gs', r'gt', r'gu', r'gw', r'gy',
    r'hk', r'hm', r'hn', r'hr', r'ht', r'hu',
    
    # I - J - K
    r'ie', r'im', r'iq', r'ir',
    r'jm', r'jo', r'jp',
    r'ke', r'kg', r'kh', r'ki', r'km', r'kn', r'kp', r'kr', r'kw', r'ky', r'kz',
    
    # L - M
    r'lb', r'lc', r'lk', r'lr', r'ls', r'lt', r'lv', r'ly',
    r'mc', r'md', r'mg', r'mh', r'mk', r'ml', r'mm', r'mn', r'mo', r'mp', r'mq', r'ms', r'mt', r'mu', r'mv', r'mw', r'mx', r'mz',
    
    # N - O - P - Q
    r'na', r'nc', r'ng', r'np', r'nr', r'nz',
    r'om',
    r'pf', r'pg', r'pk', r'pl', r'pn', r'ps', r'pt', r'py',
    r'qa',
    
    # R - S
    r'rs', r'rw',
    r'sb', r'sc', r'sd', r'sg', r'sh', r'sj', r'sk', r'sl', r'sm', r'sn', r'sr', r'st', r'sv', r'sy', r'sz',
    
    # T - U
    r'tc', r'td', r'tf', r'tg', r'th', r'tj', r'tk', r'tl', r'tm', r'tn', r'tr', r'tt', r'tw', r'tz',
    r'ua', r'ug', r'uy', r'uz',
    
    # V - W - Y - Z
    r've', r'vg', r'vi', r'vn',
    r'wf',
    r'yt',
    r'za', r'zm', r'zw'
]