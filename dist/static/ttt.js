(function() {
  function ttt($scope, $http) {
    $scope.getGame = function() {
      $http.get('/api/?game_id=' + $scope.game_id)
         .success(function(data, $location) {
            $scope.game = data;
            $scope.items = $scope.game.full_board;
      });
    };
    $scope.newGame = function() {
      var dataObj = {
        new: true
      };
      $http.post('/api/', dataObj).
        success(function(data) {
            $scope.game = data;
            $scope.items = $scope.game.full_board;
        });
    };
    $scope.playGame = function(item) {
      var dataObj = {
        game_id: $scope.game.game_id,
        move: item.square
      };
      $http.post('/api/', dataObj).
        success(function(data) {
            $scope.game = data;
            $scope.items = $scope.game.full_board;
            $scope.error = $scope.game.error_list[0];
        });
    };
  };
  angular.module("app", []).controller("ttt", ["$scope", "$http", ttt]);
})();
