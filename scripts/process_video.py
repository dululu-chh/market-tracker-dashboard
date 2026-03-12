import json
import os
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


PATH = Path("video_data/i3ZlLmYn584.en.srt")


def clean_srt(text: str) -> str:
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.isdigit() or "-->" in line:
            continue
        lines.append(line)
    return "\n".join(lines)


def learn_from_transcript(text: str) -> dict:
    prompt = f"""
你是一名資料整理專家，以下是英文逐字稿。請將它翻譯成繁體中文，並以純 JSON 格式回覆（不要多出任何前置說明或非 JSON 文字）：
{{
  "summary": "200字內摘要",
  "core_competencies": ["列出3~5項學完後的能力"],
  "tools": ["工具/平台/API/套件清單"],
  "gap_analysis": ["已就緒/需設定清單"],
  "steps": ["建議的設定順序"],
  "transcript_cn": "中文全文"
}}
逐字稿：
{text}
"""
    resp = client.responses.create(model="gpt-4.1", input=prompt)
    raw = resp.output_text or "".join(
        el.get("text", "")
        for msg in resp.output
        for el in msg.get("content", [])
        if isinstance(el, dict)
    )
    raw = raw.strip()
    print("raw response:\n", raw)
    if not raw:
        raise RuntimeError("No output from OpenAI")
    return json.loads(raw)


def main():
    if not PATH.exists():
        raise SystemExit("找不到字幕檔，先執行 yt-dlp --convert-subs srt")
    text = clean_srt(PATH.read_text(encoding="utf-8", errors="ignore"))
    result = learn_from_transcript(text)
    Path("learned_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    Path("transcript.txt").write_text(text, encoding="utf-8")
    print("生成 transcripts 和 learned_result.json")


if __name__ == "__main__":
    import os
    main()
