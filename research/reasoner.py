# research/reasoner.py
import textwrap

def make_research_answer(question, evidence_texts, niche=None):
    niche_name = niche or "your"
    question_text = (question or "").lower()
    creator_terms = ("youtube", "creator", "channel", "video", "shorts", "growth", "gaming", "content")
    is_creator_request = bool(niche) or any(term in question_text for term in creator_terms)

    if is_creator_request:
        sources = [{"title": e.get("title"), "url": e.get("url")} for e in evidence_texts[:5]]
        answer = f"""
Here is a focused YouTube growth plan for the {niche_name} niche:

1. Pick one clear viewer promise for the channel, like faster wins, better settings, funny moments, walkthroughs, or news explained simply.
2. Make 3 repeatable video series so viewers know why to return: quick tips, challenge/gameplay moments, and weekly trend reactions.
3. Improve the first 10 seconds: show the payoff first, then explain the video. Avoid long intros.
4. Use searchable titles with a human hook, for example "Best Settings for More FPS in [Game]" or "I Tried [Trend] So You Do Not Have To".
5. Design thumbnails around one idea only: one face/object, one short phrase, high contrast, and no clutter.
6. Turn every long video into 3 to 5 Shorts with a strong moment, captioned clearly, and linked back to the full video.
7. Review analytics weekly: double down on topics with high click-through rate, strong average view duration, and comments asking for more.

For your next 7 days:
- Day 1: Research 10 gaming channels in your niche and list their best-performing topics.
- Day 2: Write 5 titles before recording anything.
- Day 3: Record one long video and 3 Shorts from the same idea.
- Day 4: Make two thumbnail versions and choose the clearest one at small size.
- Day 5: Post, reply to every early comment, and pin a question.
- Day 6: Cut the best moment into a Short.
- Day 7: Check retention drop-offs and plan the next video from what viewers actually watched.
"""

        if evidence_texts:
            source_names = ", ".join([e.get("title", "source") for e in evidence_texts[:3]])
            answer += f"\nSources checked for extra context: {source_names}"

        return {
            "answer": answer.strip(),
            "sources": sources
        }

    if not evidence_texts:
        return {
            "answer": "I could not find enough useful information for that question yet.",
            "sources": []
        }

    combined = "\n\n".join([
        f"Source: {e.get('title', '')}\n{textwrap.shorten(e.get('text', ''), 1000)}"
        for e in evidence_texts[:3]
    ])

    return {
        "answer": f"Based on the available evidence:\n{combined}",
        "sources": [{"title": e.get("title"), "url": e.get("url")} for e in evidence_texts[:5]]
    }
