$(document).ready(function() {
    $("#addTags").on("click", function() {
        setTimeout( function () {
          if ($(this).hasClass("disabled")) {
            return;
          }
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
