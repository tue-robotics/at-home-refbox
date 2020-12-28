import React from 'react';
import Container from 'react-bootstrap/Container';


class Action extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      currentScore: 0
    }
  }

  increment() {
    this.setState({
      currentScore: this.state.currentScore + this.props.scoreIncrement
    });
  }

  decrement() {
    this.setState({
      currentScore: this.state.currentScore - this.props.scoreIncrement
    });
  }

  render() {
    let decrementDescription = "-"
    let incrementDescription = "+"
    let scoreDescription = String(this.state.currentScore) + '/' + String(this.props.maxScore)
    let canIncrement = this.state.currentScore < this.props.maxScore;
    let canDecrement = this.state.currentScore > 0;
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
      scoreTable: []
    };
    props.interface.registerScoreTableCallback(this.scoreTableCallback);
  }

  scoreTableCallback = (scoreTable) => {
    console.log("Setting score table, length: " + String(scoreTable.length));
    this.setState({
      scoreTable: scoreTable
    });
  }

 render() {
  const scoreTable = this.props.interface.getScoreTable();
  const actions = scoreTable.map((action, index) => {
    return (
    <Action
      key={action.key}
      description={action.description}
      scoreIncrement={action.scoreIncrement}
      maxScore={action.maxScore}
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
        <ScoreTable interface={this.props.interface}/>
      </div>
      );
  }
}

export default RefBox;