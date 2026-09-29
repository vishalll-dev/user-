const API = "/users";
const $ = (id) => document.getElementById(id);
const grid = $("grid"), statusEl = $("status"), dlg = $("dlg");

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

let users = [];

async function load() {
  const q = $("search").value.trim();
  statusEl.textContent = "Loading...";
  try {
    const res = await fetch(q ? `${API}?search=${encodeURIComponent(q)}` : API);
    users = await res.json();
    render();
  } catch (e) {
    statusEl.textContent = "Server se connect nahi ho paya. Thodi der baad try karein (server wake ho raha hoga).";
  }
}

function render() {
  statusEl.textContent = users.length ? `${users.length} user(s)` : "Koi user nahi mila.";
  grid.innerHTML = users.map((u) => `
    <div class="card">
      <h3>${esc(u.name)}</h3>
      <span class="age">Age: ${esc(u.age)}</span>
      <p>📞 ${esc(u.contact)}</p>
      <p>✉️ ${esc(u.email)}</p>
      <p>📍 ${esc(u.address)}</p>
      ${u.note ? `<p class="note">${esc(u.note)}</p>` : ""}
      <div class="row">
        <button onclick="openEdit(${u.id})">Edit</button>
        <button class="danger" onclick="removeUser(${u.id})">Delete</button>
      </div>
    </div>`).join("");
}

function openAdd() {
  $("form").reset();
  $("uid").value = "";
  $("dlgTitle").textContent = "Add User";
  dlg.showModal();
}

function openEdit(id) {
  const u = users.find((x) => x.id === id);
  if (!u) return;
  $("uid").value = u.id;
  ["name", "age", "contact", "email", "address", "note"].forEach((k) => ($(k).value = u[k]));
  $("dlgTitle").textContent = "Edit User";
  dlg.showModal();
}

async function removeUser(id) {
  if (!confirm("Is user ko delete karna hai?")) return;
  await fetch(`${API}/${id}`, { method: "DELETE" });
  load();
}

$("form").addEventListener("submit", async (e) => {
  const id = $("uid").value;
  const body = {
    name: $("name").value, age: Number($("age").value), contact: $("contact").value,
    email: $("email").value, address: $("address").value, note: $("note").value,
  };
  await fetch(id ? `${API}/${id}` : API, {
    method: id ? "PUT" : "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  load();
});

$("addBtn").onclick = openAdd;
$("cancel").onclick = () => dlg.close();
let t;
$("search").addEventListener("input", () => { clearTimeout(t); t = setTimeout(load, 300); });

load();

// Page khula ho to har 10 min server ko ping (sleep se bachane ke liye)
setInterval(() => fetch("/health").catch(() => {}), 10 * 60 * 1000);
