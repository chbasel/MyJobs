$(document).ready(function() {
    $("#addTags").on("click", function() {
        if ($(this).hasClass("disabled")) {
          return;
        }
        setTimeout( function () {

          var values = $("#p-tags").val();
          $.ajax({
            type: "GET",
            url: "/prm/view/tagging/add",
            data: {'data': values},
            success: function (data) {
              location.reload();
            }
          });
        }, 1000);
    });
});
