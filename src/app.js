$(function () {
  [$('#conferences'), $('#earlier')].forEach(function (table) {
    table.DataTable({
      autoWidth: false,
      columnDefs: [
        { responsivePriority: 1, targets: -2 }, /* event title */
        { responsivePriority: 2, targest: 0  }, /* start date */
        { responsivePriority: 3, targets: -1 }  /* event location */
      ],
      pageLength: 50,
      responsive: true
    });
  });
  $('#topics').DataTable({
    autoWidth: false,
    pageLength: 25,
    responsive: true
  });


//$(document).ready(function(){
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
        $('#search').css('display', 'inline-block');
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

