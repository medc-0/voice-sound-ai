window.addEventListener("DOMContentLoaded", () => {
  const speakBtn = document.getElementById("speak");
  const previewBtn = document.getElementById("preview");
  const text = document.getElementById("text");
  const language = document.getElementById("language");
  const gender = document.getElementById("gender");
  const voicesSel = document.getElementById("voices");
  const player = document.getElementById("player");
  const status = document.getElementById("status");

  const setStatus = (s) => {
    if (status) status.textContent = s;
  };

  async function postSpeak(payload) {
    speakBtn.disabled = true;
    previewBtn.disabled = true;
    setStatus("Generating audio...");
    try {
      const res = await fetch("/speak", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const j = await res.json();
      if (j.url) {
        player.innerHTML = `<audio controls autoplay src="${j.url}"></audio>`;
        setStatus("Playing");
      } else {
        player.textContent = JSON.stringify(j);
        setStatus("Done");
      }
    } catch (e) {
      setStatus("Error: " + e);
    }
    speakBtn.disabled = false;
    previewBtn.disabled = false;
  }

  speakBtn.addEventListener("click", async () => {
    const payload = {
      text: text.value,
      language: language.value,
      gender: gender.value,
    };
    const vid = voicesSel.value;
    if (vid) payload.voice_id = vid;
    await postSpeak(payload);
  });

  previewBtn.addEventListener("click", async () => {
    const sample = "This is a sample preview.";
    const payload = {
      text: sample,
      language: language.value,
      gender: gender.value,
    };
    const vid = voicesSel.value;
    if (vid) payload.voice_id = vid;
    await postSpeak(payload);
  });

  // load voices and populate select
  fetch("/voices")
    .then((r) => r.json())
    .then((list) => {
      voicesSel.innerHTML = "";
      const auto = document.createElement("option");
      auto.value = "";
      auto.textContent = "Auto (language/gender heuristics)";
      voicesSel.appendChild(auto);
      list.forEach((v) => {
        const opt = document.createElement("option");
        opt.value = v.id || v.name;
        opt.textContent = `${v.name || v.id} ${
          v.languages ? "- " + v.languages.join(", ") : ""
        }`;
        voicesSel.appendChild(opt);
      });
      setStatus("Voices loaded");
    })
    .catch((e) => {
      setStatus("Failed to load voices");
    });
});
