// Static data, retreived directly from the database
var scoreTable = [
  {key: 123, description: 'Enter arena', scoreIncrement: 100, maxScore: 100},
  {key: 124, description: 'Pick up drink', scoreIncrement: 100, maxScore: 300},
  {key: 125, description: 'Deliver drink', scoreIncrement: 100, maxScore: 300},
  {key: 126, description: 'Correct person', scoreIncrement: 100, maxScore: 300},
  {key: 127, description: 'Exit arena', scoreIncrement: 100, maxScore: 100},
];


var challengeInfo = {
  'Cocktail party': {
    'description': 'Enter the arena, take the orders of the three guests trying to yet your attention, serve the drinks and exit the arena',
  },
}

// State: should 'live' server side in order to keep referee and audience clients in sync
// Should support multiple arenas
var metaData = {
  'A':
    {
      'event': 'RoboCup 2021, Bordeaux, France',
      'challenge': 'Cocktail party',
      'team': 'Tech United Eindhoven',
      'attempt': 1,
    },
};


var standings = [
  {
    team: 'Tech United Eindhoven',
    played: 3,
    points: 1225,
  },
  {
    team: 'Hibikino Musashi',
    played: 3,
    points: 1175,
  },
  {
    team: 'er@sers',
    played: 3,
    points: 1125,
  },
];


var currentScores = {
  'A': {
    123: 0,
    124: 0,
    125: 0,
    126: 0,
    127: 0,
  },
}


// Use socket.io or roslib?
// See, e.g., https://medium.com/@gethylgeorge/using-socket-io-in-react-redux-app-to-handle-real-time-data-c0e734297795
class RefBoxRosInterface {
  constructor() {
      console.log('Constructing RefboxRosInterface');
      // this.scoreTableCallback = null;  // What's the JS convention for this?
  }

  registerScoreTableCallback(scoreTableCallback) {
    this.scoreTableCallback = scoreTableCallback;
    this.scoreTableCallback(scoreTable);  // Test code!!!
  }

  // ToDo: fix: get something to push to the app instead of querying
  getMetaData(arena) {
    // return metaData[arena]; // ToDo: ignorecase, errorhandling
    let data = metaData[arena];
    return data;
  }

  // ToDo: this should be score dependent...
  getScoreTable() {
    return scoreTable;
  }

  getChallengeInfo(challenge) {
    return challengeInfo[challenge];
  }

  getCurrentScore(arena) {
    return currentScores[arena];
  }

  getStandings() {
    return standings;
  }

}

export default RefBoxRosInterface;
