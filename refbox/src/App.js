// import logo from './logo.svg';

import React from 'react';
import Container from 'react-bootstrap/Container';

import './App.css';
import RefBox from './refBox';
import AudienceInfo from './audienceInfo';

// ToDo: this must obviously be split into two apps. 
class DoubleApp extends React.Component {
  render() {
    return (
      <div>
        <div>
          <Container className="p-3 bg-dark text-white">
            <RefBox/>
          </Container>
        </div>
        <p></p>
        <div>
          <Container className="p-3 bg-dark text-white">
            <AudienceInfo/>
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
