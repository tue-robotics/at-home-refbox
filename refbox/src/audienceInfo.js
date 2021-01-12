import React from 'react';
import Container from 'react-bootstrap/Container';

import Websocket from 'react-websocket';


function AudienceHeader(props) {
  let arenaDescription = 'Arena: ' + props.arena;
  let attemptDescription = 'Attempt: ' + String(props.attempt)
  return (
    <div>
      <h2>{props.event}</h2>
      <h2>{props.team}</h2>
      <p>{attemptDescription}</p>
      <p>{arenaDescription}</p>
    </div>
  );
}


function ChallengeDescription(props) {
  const defaultDescription = 'Here a description of the challenge should be displayed';
  const description = props.info.description ? props.info.description : defaultDescription;
  return (
    <div>
      <h2>{props.challenge}</h2>
      <p>{description}</p>
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
    const currentTeam = this.props.team;
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
      const style = standingItem.team === this.props.team ? 'bg-info' : 'bg-white';
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
              scoreTable={this.props.scoreTable}
              currentScore={this.props.currentScore}
              highlightScore={this.props.highlightScore}
            />
          </div>
        </div>
        <div className='col-md-6'>
          <Standings
            interface={this.props.interface}
            team={this.props.team}
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
      event: '',
      challenge: '',
      team: '',
      attempt: '',
      challengeInfo: {'description': ''},
      scoreTable: [],
      currentScore: {},
      highlightScore: null,
      standings: [],
    }
    this.onMessage = this.onMessage.bind(this);
  }

  onMessage(evt) {
    // listen to data sent from the websocket server
    const message = JSON.parse(evt);
    console.log('Message: ', message);
    this.setState({dataFromServer: message});
    if (this.state.arena in message) {
      this.updateArenaData(message[this.state.arena]);
    }
    if ('metadata' in message && this.state.arena in message.metadata) {
      this.updateMetaData(message.metadata[this.state.arena]);
    }
  }

  componentDidMount() {
  }

  updateArenaData(data) {
    if ('event' in data) {
      this.updateStaticData(data);
    }
    if ('metadata' in data) {
      this.updateMetaData(data.metadata);
    }
    if ('score_table' in data) {
      this.updateScoreTable(data.score_table)
    }
    // ToDo: this might only work if score table has already been set
    // if ('current_scores' in message && this.state.arena in message.current_scores) {
    if ('current_scores' in data) {
      this.updateScores(data.current_scores);
    }
    if ('standings' in data) {
        this.setState({standings: data.standings})
    }
  }

  updateStaticData(data) {
    this.setState({
      event: data.event,
    });
  }

  updateMetaData(metadata) {
    this.setState({
      challenge: metadata.challenge,
      team: metadata.team,
      attempt: metadata.attempt,
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
        <Websocket url='ws://localhost:6789' onMessage={this.onMessage} reconnect={true} />
        <AudienceHeader
          event={this.state.event}
          arena={this.state.arena}
          team={this.state.team}
          attempt={this.state.attempt}
        />
        <p></p>
        <ChallengeDescription
          challenge={this.state.challenge}
          info={this.state.challengeInfo}
        />
        <p></p>
        <AudienceTables
          team={this.state.team}
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
