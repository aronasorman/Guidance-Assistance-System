$(document).ready(function() {
    $("input#add").click(function () {
	var selected = $("select#section_drop option:selected");
	$("select#selected_drop").append(selected);
    });

    $("input#remove").click(function () {
	var selected = $("select#selected_drop option:selected");
	$("select#section_drop").append(selected);
    });

    $("#tanginanyonglahat").submit(function() {
	$('select#selected_drop option').attr('selected', true);
	return true;
    });
});