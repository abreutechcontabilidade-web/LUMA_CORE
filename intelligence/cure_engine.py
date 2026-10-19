# -*- coding: utf-8 -*-
import re

def higienizar_miolo(html: str) -> str:
    if not html: return ""
    html = re.sub(r'```[a-z]*\n?', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<!DOCTYPE html>|<html[^>]*>|</html>|<head[^>]*>|</head>|<body[^>]*>|</body>', '', html, flags=re.IGNORECASE)
    return html.strip()
