import React from 'react';
import Button from 'react-bootstrap/Button';
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
    // ToDo: replace buttons by bootstrap buttons
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


const AVAILABLE_TEAMS = [
  'Tech United Eindhoven',
  'Hibikino Musashi',
  'er@sers',
  'Tiny Boy',
]


class SettingSelector extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      configuring: false,
      current: props.current,
    };
  }

  onSelect = (choice) => {
    this.setState({current: choice, configuring: false});
    this.props.onSelect(this.props.setting, choice);
  }

  render() {
    if (this.state.configuring) {
      return this.renderOptions();
    } else {
      return this.renderCurrent();
    }
  }

  renderOptions() {
    const options = this.props.options.map((option) => {
      return (
        <Button
          variant='outline-secondary'
          block
          onClick={() => this.onSelect(option)}
          key={option}
        >
          {option}
        </Button>
      );
    })
    return (
      <Container className='p3 mt-2 mb-2 bg-white text-secondary'>
        <div>Select team:</div>
        <div>{options}</div>
      </Container>
    ) 
  }

  renderCurrent() {
    const description = this.props.prefix ? this.props.prefix + this.props.current : this.props.current;
    const pending = this.state.current && this.props.current !== this.state.current;
    // console.log(this.props.setting, this.props.current, this.state.current, 'pending: ', pending);
    // console.log(this.state);
    return (
      <Button
        variant='secondary'
        block onClick={() => this.setState({configuring: true})}
        disabled={pending}
      >
        {description}
      </Button>
    )
  }

}


class MetaDataSelector extends React.Component {
  render() {
    const available_challenges = ['Cocktail party'];
    const available_attempts = [1];
    return (
      <Container className='p-3 mt-2 bg-primary text-white'>
        <SettingSelector 
          setting='challenge'
          options={available_challenges}
          current={this.props.challenge}
          onSelect={this.props.onSelect}
        />
        <SettingSelector 
          setting='team'
          options={AVAILABLE_TEAMS}
          current={this.props.team}
          onSelect={this.props.onSelect}
        />
        <SettingSelector 
          setting='attempt'
          options={available_attempts}
          current={this.props.attempt}
          prefix='Attempt: '
          onSelect={this.props.onSelect}
        />
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
      console.log('Message: ', message);
      this.setState({dataFromServer: message})
      if (this.state.arena in message) {
        this.updateArenaData(message[this.state.arena]);
      }
    }

    this.ws.onclose = () => {
      console.log('disconnected')
      // automatically try to reconnect on connection loss
    }

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
    this.setState({
      currentScore: data
    });
  }

  sendScore = (key, value) => {
    this.sendData('score', key, value);
  }

  sendSetting = (key, value) => {
    this.sendData('setting', key, value);
  }

  sendData = (data_key, key, value) => {
    // let msg_data = {'arena': this.state.arena}
    let arena_data = {}
    arena_data[data_key] = {};
    arena_data[data_key][key] = value;
    let msg_data = {}
    msg_data[this.state.arena] = arena_data
    this.sendMessage(msg_data);
  }

  sendMessage = (data) => {
    try {
        this.ws.send(JSON.stringify(data));
    } catch (error) {
        console.log(error) // catch error
    }
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
          onSelect={this.sendSetting}
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