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
  render() {
    const scoreTable = this.props.scoreTable;
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
  getCurrentScore() {
    let currentScore = 0;
    for (var key in this.props.currentScore) {
      currentScore += this.props.currentScore[key];
    }
    return currentScore;
  }

  getVirtualStanding() {
    const currentStanding = this.props.standings;
    const currentScore = this.getCurrentScore();
    const currentTeam = this.props.metadata.team;
    let virtualStanding = currentStanding.map((standingItem) => {
      let updatedItem = {
        team: standingItem.team,
        played: standingItem.played,
        points: standingItem.points,
      }
      if (standingItem.team === currentTeam) {
        updatedItem.points += currentScore;
        updatedItem.played += 1;
      }
      return (updatedItem);
    });
    return (virtualStanding);
  }

  render() {
    // ToDo: implement other score systems (best of two, etc.)
    const virtualStanding = this.getVirtualStanding();
    virtualStanding.sort((a, b) => (a.points > b.points) ? -1 : ((b.points > a.points) ? 1 : 0));

    const rows = virtualStanding.map((standingItem, idx) => {
      const style = standingItem.team === this.props.metadata.team ? 'bg-info' : 'bg-white';
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
              scoreTable={this.props.scoreTable}
              currentScore={this.props.currentScore}
              highlightScore={this.props.highlightScore}
            />
          </div>
        </div>
        <div className='col-md-6'>
          <Standings 
            interface={this.props.interface}
            metadata={this.props.metadata}
            standings={this.props.standings}
            currentScore={this.props.currentScore}
          />
        </div>
      </div>
    );
  }
}


class AudienceInfo extends React.Component {
  constructor(props) {
    super(props);
    const arena = 'A';  // ToDo: don't hardcode arena
    this.state = {
      arena: arena,
      metadata: { // ToDo: similar to refbox
        event: '',
        challenge: '',
        team: '',
        attempt: '',
      },
      challengeInfo: {'description': ''},
      scoreTable: [],
      currentScore: {},
      highlightScore: null,
      standings: [],
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
      console.log('Message: ', message);
      this.setState({dataFromServer: message})
      if ('metadata' in message && this.state.arena in message.metadata) {
        this.updateMetaData(message.metadata[this.state.arena])
      }
      // ToDo: this only works if metadata has already been set...
      if ('challenge_info' in message && this.state.metadata.challenge in message.challenge_info) {
        this.setState({challengeInfo: message.challenge_info[this.state.metadata.challenge]});
      }
      if ('score_table' in message) {
        this.updateScoreTable(message.score_table)
      }
      // ToDo: this might only work if score table has already been set
      if ('current_scores' in message && this.state.arena in message.current_scores) {
        this.updateScores(message.current_scores[this.state.arena]);
      }
      if ('standings' in message) {
        this.setState({standings: message.standings})
      }
    }

    this.ws.onclose = () => {
      console.log('disconnected')
      // automatically try to reconnect on connection loss
    }

  }

  updateMetaData(metadata) {
    this.setState({
      metadata: metadata,
    })
  }

  updateScoreTable(data) {
    this.setState({scoreTable: data});
  }

  updateScores(data) {
    let newScore = data;
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
          scoreTable={this.state.scoreTable}
          currentScore={this.state.currentScore}
          highlightScore={this.state.highlightScore}
          standings={this.state.standings}
        />
      </div>
    );
  }
}

export default AudienceInfo;