// import logo from './logo.svg';

import React from 'react';
import Container from 'react-bootstrap/Container';

import './App.css';
import RefBox from './refBox';
import AudienceInfo from './audienceInfo';
import RefBoxRosInterface from './refboxRosInterface';

// ToDo: this must obviously be split into two apps. 
class DoubleApp extends React.Component {
  render() {
    let serverInterface = new RefBoxRosInterface();
    return (
      <div>
        <div>
          <Container className="p-3 bg-dark text-white">
            <RefBox interface={serverInterface}/>
          </Container>
        </div>
        <p></p>
        <div>
          <Container className="p-3 bg-dark text-white">
            <AudienceInfo interface={serverInterface}/>
          </Container>
        </div>
      </div>
      );
  }
}


const App = () => (
  <DoubleApp/>
);

export default App;
