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


// Use socket.io or roslib?
// See, e.g., https://medium.com/@gethylgeorge/using-socket-io-in-react-redux-app-to-handle-real-time-data-c0e734297795
class RefBoxRosInterface {
  constructor() {
      console.log('Constructing RefboxRosInterface');
      // this.scoreTableCallback = null;  // What's the JS convention for this?
  }

  getStandings() {
    return standings;
  }

}

export default RefBoxRosInterface;
