import React from 'react';
import Container from 'react-bootstrap/Container';


class Action extends React.Component {
  increment() {
    let newScore = this.props.currentScore + this.props.scoreIncrement;
    this.props.onScore(this.props.key2, newScore);
  }

  decrement() {
    let newScore = this.props.currentScore - this.props.scoreIncrement
    this.props.onScore(this.props.key2, newScore);
  }

  render() {
    let currentScore = this.props.currentScore;
    let decrementDescription = "-"
    let incrementDescription = "+"
    let scoreDescription = String(currentScore) + '/' + String(this.props.maxScore)
    let canIncrement = currentScore < this.props.maxScore;
    let canDecrement = currentScore > 0;
    return (
      <tr>
        <th>{this.props.description}</th>
        <th style={{textAlign: 'center'}}><button onClick={() => this.decrement()} disabled={!canDecrement}>{decrementDescription}</button></th>
        <th style={{textAlign: 'center'}}>{scoreDescription}</th>
        <th style={{textAlign: 'center'}}><button onClick={() => this.increment()} disabled={!canIncrement}>{incrementDescription}</button></th>
      </tr>
    );
  }
}


class ScoreTable extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      scoreTable: props.interface.getScoreTable(),
    };

  }

 render() {
  const scoreTable = this.state.scoreTable;
  const actions = scoreTable.map((action, index) => {
    let scoreValue = this.props.currentScore ? this.props.currentScore[action.key] : 0; 
    return (
    <Action
      key={action.key}
      key2={action.key}
      description={action.description}
      scoreIncrement={action.scoreIncrement}
      currentScore={scoreValue}
      maxScore={action.maxScore}
      onScore={this.props.onScore}
    />
    );  
  });
  // <div>{actions}</div>
  return (
    <Container className='p-3 bg-white text-primary'>
      <table className="table table-bordered">
        <tbody>
          {actions}
        </tbody>
      </table>    
    </Container>
  );
  } 
}


class RefBox extends React.Component {
  constructor(props) {
    super(props);
    let arena = 'A';  // ToDo: don't hardcode arena
    let metadata = props.interface.getMetaData(arena);
    this.state = {
      event: metadata.event,
      arena: arena,
      challenge: metadata.challenge,
      team: metadata.team,
      attempt: metadata.attempt,
    }
  }

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
    this.setState({
      currentScore: data[this.state.arena]
    });
  }

  sendMessage = (data) => {
    try {
        this.ws.send(JSON.stringify(data));
    } catch (error) {
        console.log(error) // catch error
    }
  }

  // ToDo: only send the score 'event'
  sendScore = (key, value) => {
    let data = {
      'arena': this.state.arena,
      'score': {
        'key': key,
        'value': value,
      }
    }
    this.sendMessage(data);
  }

  render()
  {
    let arenaDescription = 'Arena: ' + this.state.arena;
    let attemptDescription = 'Attempt: ' + String(this.state.attempt)
    return (
      <div>
        <div>{this.state.event}</div>
        <div>{arenaDescription}</div>
        <div>{this.state.challenge}</div>
        <div>{this.state.team}</div>
        <div>{attemptDescription}</div>
        <ScoreTable 
          interface={this.props.interface}
          websocket={this.ws}
          onScore={this.sendScore}
          currentScore={this.state.currentScore}
        />
      </div>
      );
  }
}

export default RefBox;