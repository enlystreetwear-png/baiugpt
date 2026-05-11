const API_KEY_STORAGE = "baiugpt_api_key";
const messagesEl = document.querySelector("#messages");
const formEl = document.querySelector("#chatForm");
const promptEl = document.querySelector("#promptInput");
const sendBtn = document.querySelector("#sendBtn");
const statusGrid = document.querySelector("#statusGrid");
const nicheInput = document.querySelector("#nicheInput");
const langInput = document.querySelector("#langInput");
const apiKeyInput = document.querySelector("#apiKeyInput");
const newChatBtn = document.querySelector("#newChatBtn");

const savedKey = localStorage.getItem(API_KEY_STORAGE);
if (savedKey) apiKeyInput.value = savedKey;

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function sourceList(sources) {
  if (!sources || !sources.length) return "";
  const items = sources.slice(0, 6).map((source) => {
    const title = escapeHtml(source.title || source.url || "Source");
    const url = escapeHtml(source.url || "#");
    return `<div><a href="${url}" target="_blank" rel="noreferrer">${title}</a></div>`;
  }).join("");
  return `<div><strong>Sources</strong>${items}</div>`;
}

function curiosityBlock(curiosity) {
  if (!curiosity) return "";
  const selfQuestions = (curiosity.selfQuestions || [])
    .map((item) => `<div>Why: ${escapeHtml(item)}</div>`)
    .join("");
  const askUser = (curiosity.askUserNext || [])
    .map((item) => `<div>Next: ${escapeHtml(item)}</div>`)
    .join("");
  const learned = curiosity.learnedSignals ?? 0;
  return `<div><strong>Native curiosity</strong><div>Learned signals: ${learned}</div>${selfQuestions}${askUser}</div>`;
}

function addMessage(role, text, meta = {}) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;
  wrapper.innerHTML = `
    <div class="bubble">${escapeHtml(text)}</div>
    <div class="meta">
      ${curiosityBlock(meta.curiosity)}
      ${sourceList(meta.sources)}
    </div>
  `;
  messagesEl.appendChild(wrapper);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setStatus(status) {
  const device = status.device || {};
  const gpuText = device.gpuName || "CPU";
  const gpuCount = device.gpuCount || 0;
  const mode = status.mode || "native-local";
  statusGrid.innerHTML = `
    <span class="pill good">${escapeHtml(mode)}</span>
    <span class="pill ${device.cudaAvailable ? "good" : ""}">${device.cudaAvailable ? "CUDA" : "CPU"}: ${escapeHtml(gpuText)}</span>
    <span class="pill">GPUs: ${gpuCount} / current single-GPU mode</span>
    <span class="pill">Memory: ${status.memoryCount || 0}</span>
    <span class="pill">Training: ${status.trainingExampleCount || 0}</span>
  `;
}

async function loadStatus() {
  const response = await fetch("/native/status", {
    headers: { "x-api-key": apiKeyInput.value },
  });
  const data = await response.json();
  setStatus(data);
}

async function sendPrompt(prompt) {
  const body = {
    prompt,
    niche: nicheInput.value || "content creation",
    lang: langInput.value || "English",
  };
  const response = await fetch("/ai/native-generate", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": apiKeyInput.value,
    },
    body: JSON.stringify(body),
  });
  return response.json();
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const prompt = promptEl.value.trim();
  if (!prompt) return;

  localStorage.setItem(API_KEY_STORAGE, apiKeyInput.value);
  addMessage("user", prompt);
  promptEl.value = "";
  sendBtn.disabled = true;
  sendBtn.textContent = "Thinking";

  try {
    const data = await sendPrompt(prompt);
    if (data.error) {
      addMessage("assistant", `Error: ${data.error}`);
    } else {
      addMessage("assistant", data.answer || "No answer returned.", {
        sources: data.sources || [],
        curiosity: data.curiosity,
      });
      await loadStatus();
    }
  } catch (error) {
    addMessage("assistant", `Request failed: ${error.message}`);
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = "Send";
    promptEl.focus();
  }
});

newChatBtn.addEventListener("click", () => {
  messagesEl.innerHTML = "";
  addMessage("assistant", "New local BaiuGPT chat ready. Ask normally. I will skip useless searches, learn from useful questions, and keep the answer in general-purpose mode unless you choose a niche.");
});

promptEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    formEl.requestSubmit();
  }
});

loadStatus().catch(() => {
  statusGrid.innerHTML = `<span class="pill">Start BaiuGPT API, then refresh</span>`;
});

addMessage("assistant", "BaiuGPT native chat is ready. One RTX 4060 is active now. Use General Purpose for normal chat, or type a niche like Tech Reviews when you want TubeCoach-style planning.");
