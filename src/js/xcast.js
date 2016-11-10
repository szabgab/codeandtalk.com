$(document).ready(function(){
    var availableTags = [];
    var mapping = {}

    $.getJSON("/search.json", function( result ) {
        //console.log(result);
        //console.log(result.length)
        mapping = result;
        for (var key in result) {
            if (result.hasOwnProperty(key)) {
                availableTags.push(key);
            }
        }
        availableTags.sort();
        //console.log(availableTags);

    //    $('#q').css('display', 'inline');
        $('#search').css('display', 'inline');
        $( "#q" ).autocomplete({
          source: availableTags
        });
        $('#search').submit(function(e) {
            console.log('submit');
            var term = $('#q').val();
            e.preventDefault();
            if (mapping[term]) { 
                window.location.href = mapping[term];
            }
        });

    });

});
// vim: expandtab
