#!/usr/bin/env python3
"""Valida o treinos.json do app de treino.

Uso:
  python validar.py treinos.json              # só estrutura (offline)
  python validar.py treinos.json --online     # também confere cada vídeo no YouTube
  python validar.py treinos.json --online --corrigir   # remove vídeos que não existem ou não podem ser incorporados

Saída: lista de erros (código de saída 1) ou "OK" (código 0).
A checagem online usa o oEmbed do YouTube: 200 = existe e pode ser incorporado;
401/403/404 = removido, privado ou com incorporação desativada. Falhas de rede
não removem nada, só ficam marcadas como "não verificado".
"""
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
EX_ID = re.compile(r"^[A-Za-z0-9_-]+$")
VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")


def video_id(v):
    return v if isinstance(v, str) else (v or {}).get("id", "")


def validar_estrutura(data):
    erros = []
    treinos = data.get("treinos") if isinstance(data, dict) else None
    if not isinstance(treinos, list) or not treinos:
        return ["raiz: precisa ter a lista 'treinos' com pelo menos um treino"]

    ids_treino = set()
    for t in treinos:
        tid = t.get("id", "?")
        loc = f"treino '{tid}'"
        if not SLUG.match(str(tid)):
            erros.append(f"{loc}: 'id' deve usar letras minúsculas, números e hífen")
        if tid in ids_treino:
            erros.append(f"{loc}: id repetido")
        ids_treino.add(tid)
        if not t.get("nome"):
            erros.append(f"{loc}: falta 'nome'")
        fases = t.get("fases")
        if not isinstance(fases, list) or not fases:
            erros.append(f"{loc}: precisa de pelo menos uma fase")
            continue

        ids_fase = set()
        for f in fases:
            fid = f.get("id", "?")
            floc = f"{loc} > fase '{fid}'"
            if not EX_ID.match(str(fid)):
                erros.append(f"{floc}: 'id' inválido")
            if fid in ids_fase:
                erros.append(f"{floc}: id de fase repetido")
            ids_fase.add(fid)
            for campo in ("aba", "titulo"):
                if not f.get(campo):
                    erros.append(f"{floc}: falta '{campo}'")
            if "rounds" in f and not (isinstance(f["rounds"], int) and f["rounds"] >= 1):
                erros.append(f"{floc}: 'rounds' deve ser inteiro >= 1")
            if "descanso" in f and not (isinstance(f["descanso"], int) and f["descanso"] > 0):
                erros.append(f"{floc}: 'descanso' deve ser inteiro > 0 (segundos)")
            if "tabata" in f:
                tb = f["tabata"]
                for campo in ("rounds", "trabalho", "descanso"):
                    if not (isinstance(tb, dict) and isinstance(tb.get(campo), int) and tb[campo] > 0):
                        erros.append(f"{floc}: tabata.{campo} deve ser inteiro > 0")
            if "rounds" in f and "tabata" in f:
                erros.append(f"{floc}: use 'rounds' OU 'tabata', não os dois")

            exs = f.get("exercicios")
            if not isinstance(exs, list) or not exs:
                erros.append(f"{floc}: precisa de pelo menos um exercício")
                continue
            ids_ex = set()
            for e in exs:
                eid = e.get("id", "?")
                eloc = f"{floc} > exercício '{eid}'"
                if not EX_ID.match(str(eid)):
                    erros.append(f"{eloc}: 'id' inválido (use letras, números, _ ou -)")
                if eid in ids_ex:
                    erros.append(f"{eloc}: id repetido na fase")
                ids_ex.add(eid)
                for campo in ("nome", "prescricao"):
                    if not e.get(campo):
                        erros.append(f"{eloc}: falta '{campo}'")
                if "timer" in e:
                    tm = e["timer"]
                    if not isinstance(tm, list) or not tm:
                        erros.append(f"{eloc}: 'timer' deve ser uma lista não vazia")
                    else:
                        for s in tm:
                            if not (isinstance(s, dict) and s.get("label") and isinstance(s.get("segundos"), int) and s["segundos"] > 0):
                                erros.append(f"{eloc}: cada item de 'timer' precisa de 'label' e 'segundos' (inteiro > 0)")
                vids = e.get("videos", [])
                if not isinstance(vids, list):
                    erros.append(f"{eloc}: 'videos' deve ser uma lista")
                    continue
                vistos = set()
                for v in vids:
                    vid = video_id(v)
                    if not VIDEO_ID.match(vid):
                        erros.append(f"{eloc}: ID de vídeo inválido '{vid}' (são 11 caracteres)")
                    if vid in vistos:
                        erros.append(f"{eloc}: vídeo repetido '{vid}'")
                    vistos.add(vid)
                    if isinstance(v, dict) and v.get("tipo", "short") not in ("short", "video"):
                        erros.append(f"{eloc}: tipo de vídeo deve ser 'short' ou 'video'")
                if len(vids) > 5:
                    erros.append(f"{eloc}: mais de 5 vídeos deixa o carrossel pesado")
                if not e.get("busca"):
                    erros.append(f"{eloc}: falta 'busca' (termo do link 'Buscar no YouTube')")
    return erros


def checar_video(vid):
    """Retorna 'ok', 'invalido' ou 'desconhecido'."""
    url = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(
        "https://www.youtube.com/watch?v=" + vid, safe=""
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return "ok" if r.status == 200 else "desconhecido"
    except urllib.error.HTTPError as e:
        return "invalido" if e.code in (401, 403, 404) else "desconhecido"
    except Exception:
        return "desconhecido"


def checar_online(data, corrigir):
    problemas, removidos = [], 0
    for t in data["treinos"]:
        for f in t["fases"]:
            for e in f["exercicios"]:
                novos = []
                for v in e.get("videos", []):
                    vid = video_id(v)
                    estado = checar_video(vid)
                    rotulo = f"{t['id']}/{f['id']}/{e['id']} {vid}"
                    if estado == "invalido":
                        problemas.append(f"vídeo indisponível ou sem incorporação: {rotulo}")
                        if corrigir:
                            removidos += 1
                            continue
                    elif estado == "desconhecido":
                        print(f"  aviso: não consegui verificar {rotulo}")
                    novos.append(v)
                if corrigir:
                    e["videos"] = novos
    return problemas, removidos


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    online = "--online" in sys.argv
    corrigir = "--corrigir" in sys.argv
    if not args:
        print(__doc__)
        return 2
    caminho = args[0]
    try:
        with open(caminho, encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:
        print(f"ERRO: não consegui ler {caminho}: {exc}")
        return 1

    erros = validar_estrutura(data)
    if erros:
        print("ERROS DE ESTRUTURA:")
        for e in erros:
            print("  -", e)
        return 1

    if online:
        problemas, removidos = checar_online(data, corrigir)
        if problemas:
            print("PROBLEMAS COM VÍDEOS:")
            for p in problemas:
                print("  -", p)
            if corrigir:
                with open(caminho, "w", encoding="utf-8") as fh:
                    json.dump(data, fh, ensure_ascii=False, indent=2)
                    fh.write("\n")
                print(f"{removidos} vídeo(s) removido(s) do arquivo. Procure substitutos para os exercícios afetados.")
                return 0
            return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
