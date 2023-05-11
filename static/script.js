$(document).ready(function() {
    $("#askButton").on("click", function(event) {
    event.preventDefault();
    var question = $("#questionInput").val();
    $.ajax({
    url: "{{ url_for('answer') }}",
    type: "POST",
    data: { question: question },
    success: function(response) {
    $("#answer").text(response.answer);
    }
    });
    });
    });