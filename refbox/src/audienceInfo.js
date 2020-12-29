import React from 'react';
import Container from 'react-bootstrap/Container';


function AudienceHeader(props) {
  let arenaDescription = 'Arena: ' + props.metadata.arena;
  let attemptDescription = 'Attempt: ' + String(props.metadata.attempt)
  return (
    <div>
      <h2>{props.metadata.event}</h2>
      <h2>{props.metadata.team}</h2>
      <p>{attemptDescription}</p>
      <p>{arenaDescription}</p>
    </div>
  );
}  


function ChallengeDescription(props) {
  return (
    <div>
      <h2>{props.metadata.challenge}</h2>
      <p>{props.info.description}</p>
    </div>
  );
}


class CurrentScoreTable extends React.Component {
  constructor(props) {
    console.log('CurrentScoreTable constructor');
    super(props);
    this.state = {
      scoreTable: props.interface.getScoreTable(),
    };
  }

  render() {
    const scoreTable = this.state.scoreTable;
    const currentScore = this.props.currentScore;
    const rows = scoreTable.map((scoreItem, idx) => {
      let scoreValue = currentScore ? currentScore[scoreItem.key] : 0;
      const score = String(scoreValue) + '/' + String(scoreItem.maxScore);
      let style = scoreItem.key === this.props.highlightScore ? 'bg-info' : 'bg-white';
      return (
        <tr key={idx} className={style}>
          <th>{scoreItem.description}</th>
          <th style={{textAlign: 'center'}}>{score}</th>
        </tr>
      );
    });

    return (
      <Container className="p-3 bg-white text-primary">
        <table className="table table-bordered">
          <thead>
            <tr>
              <th>Description</th><th>Points</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
      </Container>
    );
  }
}


class Standings extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      currentStanding: props.interface.getStandings(),
      currentScore: 0,
    };
  }

  render() {
    // ToDo: there's bug here that keeps increasing the 'played' (something with references and values)
    // ToDo: implement other score systems (best of two, etc.)
    let currentStanding = this.state.currentStanding;
    currentStanding = currentStanding.map((standingItem) => {
      if (standingItem.team === this.props.metadata.team) {
        standingItem.points += this.state.currentScore;
        standingItem.played += 1;
      }
      return (standingItem);
    });
    currentStanding.sort((a, b) => (a.points > b.points) ? -1 : ((b.points > a.points) ? 1 : 0));

    const rows = currentStanding.map((standingItem, idx) => {
      let style = standingItem.team === this.props.metadata.team ? 'bg-info' : 'bg-white';
      return (
        <tr key={idx} className={style}>
          <th>{standingItem.team}</th>
          <th style={{textAlign: 'right'}}>{standingItem.played}</th>
          <th style={{textAlign: 'right'}}>{standingItem.points}</th>
        </tr>
      );
    });

    return (
      <Container className='p-3 bg-white text-primary'>
        <table className='table table-bordered'>
          <thead>
            <tr>
              <th>Team</th><th>Played</th><th>Points</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
      </Container>
    );
  }
}


class AudienceTables extends React.Component {
  render() {
    return (
      <div className='row'>
        <div className='col-md-6'>
          <div className='container'>
            <CurrentScoreTable
              interface={this.props.interface}
              metadata={this.props.metadata}
              currentScore={this.props.currentScore}
              highlightScore={this.props.highlightScore}
            />
          </div>
        </div>
        <div className='col-md-6'>
          <Standings 
            interface={this.props.interface}
            metadata={this.props.metadata}
          />
        </div>
      </div>
    );
  }
}


class AudienceInfo extends React.Component {
  constructor(props) {
    super(props);
    let arena = 'A';  // ToDo: don't hardcode arena
    let metadata = props.interface.getMetaData(arena);
    let challengeInfo = props.interface.getChallengeInfo(metadata.challenge);
    this.state = {
      metadata: {
        event: metadata.event,
        arena: arena,
        challenge: metadata.challenge,
        team: metadata.team,
        attempt: metadata.attempt,
      },
      challengeInfo: challengeInfo,
      currentScore: {},
      highlightScore: null,
    } 
  }

  // Websocket use based on 
  // https://dev.to/finallynero/using-websockets-in-react-4fkp
  // instance of websocket connection as a class property
  ws = new WebSocket('ws://localhost:6789')

  componentDidMount() {
    this.ws.onopen = () => {
      // on connecting, do nothing but log it to the console
      console.log('connected')
    }

    this.ws.onmessage = evt => {
      // listen to data sent from the websocket server
      const message = JSON.parse(evt.data)
      this.setState({dataFromServer: message})
      if ('current_scores' in message) {
        this.updateScores(message.current_scores);
      }
    }

    this.ws.onclose = () => {
      console.log('disconnected')
      // automatically try to reconnect on connection loss
    }

  }

  updateScores(data) {
    let newScore = data[this.state.metadata.arena];
    let changedScore = null;
    for (var key in newScore) {
      if (newScore[key] !== this.state.currentScore[key]) {
        changedScore = parseInt(key);
      }
    }
    this.setState({
      currentScore: newScore,
      highlightScore: changedScore,
    });
    setTimeout(function() { //Start the timer
      this.setState({highlightScore: null}); //After 1 second, disable highlight
    }.bind(this), 1000);
  }

  render() {
    return (
      <div>
        <AudienceHeader metadata={this.state.metadata}/>
        <p></p>
        <ChallengeDescription
          metadata={this.state.metadata}
          info={this.state.challengeInfo}
        />
        <p></p>
        <AudienceTables
          metadata={this.state.metadata}
          interface={this.props.interface}
          currentScore={this.state.currentScore}
          highlightScore={this.state.highlightScore}
        />
      </div>
    );
  }
}

export default AudienceInfo;