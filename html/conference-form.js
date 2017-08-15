/*function ctrl($scope) {
    var array = conf.languages.split(',');
    $scope.conf["languages"] = [];
    $scope.conf["languages"].push({});
    $scope.update = angular.copy.conf;
}
*/
/*function addNewLocation() {
    var currLocation =  $('#locationContainer').html();
    var newLocation = "<input type=\"text\" name=\"location\"/>"
    $('#locationContainer').html(currLocation + " " + newLocation)
    
}*/

function createJSONtext() {
    var outputJSON={};
    var separator_re = /[, ;]+/;
    $('.field').each(function() {
       outputJSON[$(this).attr("name")]= $(this).val();
       
    });
    
    $('.arrayField').each(function() {
       console.log('array');
       var array = $(this).val().split(separator_re);
       outputJSON[$(this).attr("name")]= array;
       
    });
        
    $('.complexField').each(function() {
      console.log('complex field');
       var name = $(this).attr('data-name');
       console.log(name);
       var obj = {}
       $(this).children('.nestedField').each(function() {
               obj[$(this).attr("name")]= $(this).val();
           });
       outputJSON[name]= obj;
 
    });
  
    
    $('#json-out').val( JSON.stringify (outputJSON,null, '\t'));
}