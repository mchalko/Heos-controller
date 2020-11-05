
function setIndicator(indicator, state) {
    indicator.removeClass(["cross-mark", "check-mark", "spinner-border"]);
    if (state == "none") {
        indicator.css("display", "none");
    } else {
        indicator.css("display", "inline-block");
        if (state == "fail") {
            indicator.addClass("cross-mark");
        } else if (state == "success") {
            indicator.addClass("check-mark");
        } else {
            indicator.addClass("spinner-border");
        }
    }
}

$(document).ready(function () {
    $("#menu-toggle").click(function (e) {
        e.preventDefault();
        $("#wrapper").toggleClass("toggled");
    });
    $(".menu-item").click(function (e) {
        e.preventDefault();
        $(".content-tab").css("display", "none");
        $($(this).attr("href")).css("display", "block");
    });
    $(".btn-form").click(function (e) {
        e.preventDefault();

        var form = $(this).closest("form");
        var indicator = $(this).find(".indicator:first");
        if (form[0].checkValidity() === true) {
            var data = JSON.stringify(form.serializeJSON());
            setIndicator(indicator, "");

            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4 && xhr.status != 200) {
                    setIndicator(indicator, "fail");
                } else if (xhr.readyState == 4 && xhr.status == 200) {
                    setIndicator(indicator, "success");
                }
            };
            xhr.open("POST", form.attr("action"));
            xhr.send();
        } else {
            e.stopPropagation();
        }
        form.addClass('was-validated');
    });
});