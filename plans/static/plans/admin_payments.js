document.addEventListener("DOMContentLoaded", () => {
    function showToast(msg, success = true) {
        const t = document.createElement("div");
        t.textContent = msg;
        t.style.position = "fixed";
        t.style.bottom = "30px";
        t.style.right = "30px";
        t.style.padding = "12px 18px";
        t.style.borderRadius = "6px";
        t.style.background = success ? "#28a745" : "#e74c3c";
        t.style.color = "white";
        t.style.zIndex = 9999;
        document.body.appendChild(t);
        setTimeout(() => t.remove(), 2000);
    }

    async function post(url) {
        const res = await fetch(url, {method: "POST", headers: {"X-CSRFToken": window.CSRF_TOKEN}});
        return res.json();
    }

    // approve single
    document.querySelectorAll(".approve-btn").forEach(btn => {
        btn.onclick = async () => {
            const id = btn.dataset.id;
            const data = await post(`/admin/payments/${id}/ajax/approve/`);
            showToast(data.msg, data.ok);
            if (data.ok) {
                btn.parentElement.parentElement.style.opacity = 0.5;
            }
        };
    });

    // reject single
    document.querySelectorAll(".reject-btn").forEach(btn => {
        btn.onclick = async () => {
            const id = btn.dataset.id;
            const data = await post(`/admin/payments/${id}/ajax/reject/`);
            showToast(data.msg, data.ok);
            if (data.ok) {
                btn.parentElement.parentElement.style.opacity = 0.5;
            }
        };
    });

    // approve all
    const approveAllBtn = document.getElementById("approve-all-btn");
    if (approveAllBtn) {
        approveAllBtn.onclick = async () => {
            const data = await post(`/admin/payments/ajax/approve_all/`);
            showToast(data.msg, true);
            location.reload();
        };
    }
});
