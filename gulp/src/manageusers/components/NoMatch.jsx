import React from 'react';

class NoMatch extends React.Component {
  render() {
    return (
      <div className="row">
        <div className="col-xs-12">
          <div className="wrapper-header">
            <h2>Not found.</h2>
          </div>
          <div className="product-card no-highlight">
            <p>Not found.</p>
          </div>
        </div>
      </div>
    );
  }
}

export default NoMatch;
