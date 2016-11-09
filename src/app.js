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
});
