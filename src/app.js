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


    // Append a Twitter logo after every quote and make it Tweetable
    $('q').each(function( item ) {
        console.log( $(this).text() );
        var status = encodeURIComponent( $(this).text() + ' ' + window.location.href );
        var event_twitter = $('#event_twitter').val()
        if (event_twitter) {
            status += ' @' + event_twitter;
        }
        var speaker_twitters = $('#speaker_twitters').val();
        if (speaker_twitters) {
            status += speaker_twitters;
        }

        var html = '<a target="_blank" href="https://twitter.com/home?status=' + status + '"><i class="fa fa-twitter"></i></a>';
        $(this).append(html);
    })

});

// vim: expandtab

