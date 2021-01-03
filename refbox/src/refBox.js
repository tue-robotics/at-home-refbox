import React from 'react';
import Container from 'react-bootstrap/Container';


class Action extends React.Component {
  increment() {
    this.props.onScore(this.props.key2, this.props.scoreIncrement);
  }

  decrement() {
    this.props.onScore(this.props.key2, -this.props.scoreIncrement);
  }

  render() {
    let currentScore = this.props.currentScore;
    let decrementDescription = "-"
    let incrementDescription = "+"
    let scoreDescription = String(currentScore) + '/' + String(this.props.maxScore)
    let canIncrement = currentScore < this.props.maxScore;
    let canDecrement = currentScore > 0;
    return (
      <tr className='text-white'>
        <th>{this.props.description}</th>
        <th style={{textAlign: 'center'}}><button onClick={() => this.decrement()} disabled={!canDecrement}>{decrementDescription}</button></th>
        <th style={{textAlign: 'center'}}>{scoreDescription}</th>
        <th style={{textAlign: 'center'}}><button onClick={() => this.increment()} disabled={!canIncrement}>{incrementDescription}</button></th>
      </tr>
    );
  }
}


class ScoreTable extends React.Component {
 render() {
  const scoreTable = this.props.scoreTable;
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
  return (
    <Container className='p-3 mt-2 bg-primary text-white'>
      <table className="table table-bordered">
        <tbody>
          {actions}
        </tbody>
      </table>    
    </Container>
  );
  } 
}


class MetaDataSelector extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      configuring: false,
    };
  }

  render() {
    const attemptDescription = 'Attempt: ' + String(this.props.attempt)
    return (
      <Container className='p-3 mt-2 bg-primary text-white'>
        <div>{this.props.challenge}</div>
        <div>{this.props.team}</div>
        <div>{attemptDescription}</div>
      </Container>
    )
  }
}


class RefBox extends React.Component {
  constructor(props) {
    super(props);
    const arena = 'A';  // ToDo: don't hardcode arena
    this.state = {
      arena: arena,
      event: '',
      challenge: '',
      team: '',
      attempt: '',
      scoreTable: [],
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
      if ('metadata' in message && this.state.arena in message.metadata) {
        this.updateMetaData(message.metadata[this.state.arena])
      }
      if ('score_table' in message) {
        this.updateScoreTable(message.score_table)
      }
      // ToDo: this might only work if score table has already been set
      if ('current_scores' in message && this.state.arena in message.current_scores) {
        this.updateScores(message.current_scores[this.state.arena]);
      }
    }

    this.ws.onclose = () => {
      console.log('disconnected')
      // automatically try to reconnect on connection loss
    }

  }

  updateMetaData(metadata) {
    this.setState({
      event: metadata.event,
      challenge: metadata.challenge,
      team: metadata.team,
      attempt: metadata.attempt,
    })
  }

  updateScoreTable(data) {
    this.setState({scoreTable: data});
  }

  updateScores(data) {
    this.setState({
      currentScore: data
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
    const data = {
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
    const arenaDescription = 'Arena: ' + this.state.arena;
    return (
      <div>
        <Container className='p-3 bg-primary text-white'>
          <div>{this.state.event}</div>
          <div>{arenaDescription}</div>
        </Container>
        <MetaDataSelector
          challenge={this.state.challenge}
          team={this.state.team}
          attempt={this.state.attempt}
        />
        <ScoreTable 
          scoreTable={this.state.scoreTable}
          onScore={this.sendScore}
          currentScore={this.state.currentScore}
        />
      </div>
      );
  }
}

export default RefBox;