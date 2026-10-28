(function () {
    var e = "https://points.fivepost.ru/widget";
    var t = "fivepost-widget-iframe";
    window.FivePostMap = {
        open: function (n) {
            if (!n || !n.apiKey) return;
            var o = document.getElementById(t);
            if (o) o.remove();
            var r = document.createElement("iframe");
            r.id = t;
            r.src = e + "/index.html?apiKey=" + encodeURIComponent(n.apiKey) + "&cms=" + encodeURIComponent(n.cms || "Custom") + "&allowedDeliveryTypes=" + encodeURIComponent((n.allowedDeliveryTypes || ["POSTAMAT", "COUNTER"]).join(","));
            r.style.position = "fixed"; r.style.top = "0"; r.style.left = "0"; r.style.width = "100%"; r.style.height = "100%"; r.style.zIndex = "999999"; r.style.border = "none";
            document.body.appendChild(r);
            window.addEventListener("message", function (e) {
                if (e.data && e.data.source === "fivepost-widget") {
                    if (e.data.action === "choose" && typeof n.onChoose === "function") n.onChoose(e.data.point);
                    if (e.data.action === "close") { var t = document.getElementById(t); if (t) t.remove(); }
                }
            });
        }
    };
})();
