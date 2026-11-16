"""Narração neural do Azure (grátis no Free F0) com o tempo de cada palavra e de cada bookmark.

Uso: python3 kit/video/narrado/voz.py r1/voz.ssml r1/voz.wav r1/voz.json
Chave: variáveis AZURE_SPEECH_KEY e AZURE_SPEECH_REGION, ou um arquivo KEY=VALOR apontado por AZURE_CHAVES
(padrão ~/.azure-voz). O cliente cola a chave no arquivo; nunca mostre nem repita a chave.
Voz padrão aprovada: pt-BR-FranciscaNeural, prosody rate +6%. Bookmarks <bookmark mark="s1"/> marcam a troca de cena.
"""
import json, sys, os
import azure.cognitiveservices.speech as sdk

arq = os.path.expanduser(os.environ.get("AZURE_CHAVES", "~/.azure-voz"))
if not os.environ.get("AZURE_SPEECH_KEY") and os.path.exists(arq):
    for l in open(arq):
        if "=" in l: k, v = l.strip().split("=", 1); os.environ[k] = v
if not os.environ.get("AZURE_SPEECH_KEY"):
    sys.exit("sem chave do Azure: peça ao cliente para salvar AZURE_SPEECH_KEY=... e AZURE_SPEECH_REGION=... no arquivo " + arq)
cfg = sdk.SpeechConfig(subscription=os.environ["AZURE_SPEECH_KEY"], region=os.environ["AZURE_SPEECH_REGION"])
pr = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
if pr:
    import urllib.parse as U; u = U.urlparse(pr); cfg.set_proxy(u.hostname, u.port, u.username, u.password)
cfg.set_speech_synthesis_output_format(sdk.SpeechSynthesisOutputFormat.Riff48Khz16BitMonoPcm)
ssml, wav, js = sys.argv[1:4]
syn = sdk.SpeechSynthesizer(speech_config=cfg, audio_config=sdk.audio.AudioOutputConfig(filename=wav))
pal, bm = [], []
def wb(e):
    if e.boundary_type == sdk.SpeechSynthesisBoundaryType.Word:
        pal.append({"w": e.text, "a": e.audio_offset / 1e7, "d": e.duration.total_seconds()})
    elif e.boundary_type == sdk.SpeechSynthesisBoundaryType.Punctuation and pal:
        pal[-1]["w"] += e.text
syn.synthesis_word_boundary.connect(wb)
syn.bookmark_reached.connect(lambda e: bm.append({"nome": e.text, "t": e.audio_offset / 1e7}))
r = syn.speak_ssml_async(open(ssml).read()).get()
if r.reason != sdk.ResultReason.SynthesizingAudioCompleted:
    print("erro", r.reason, r.cancellation_details.error_details if r.cancellation_details else ""); sys.exit(1)
json.dump({"palavras": pal, "marcas": bm, "dur": r.audio_duration.total_seconds()}, open(js, "w"), ensure_ascii=False, indent=1)
print("ok", len(pal), "palavras", round(r.audio_duration.total_seconds(), 2), "s")
