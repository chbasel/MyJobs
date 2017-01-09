import React from 'react';
import {Component} from 'react';

class NoResults extends Component {
  render() {
    const {type, errorMessage, helpErrorMessage} = this.props;
    switch (type) {
    case 'table':
      return (
        <tr className="table-no-results">
          <td colSpan="8">{errorMessage}</td>
        </tr>
      );
    case 'div':
      return (
        <div className="no-results">
          <h1>{errorMessage}</h1>
          <p>{helpErrorMessage}</p>
        </div>
      );
    default:
      return (
        <div className="no-result">
          <h1>{errorMessage}</h1>
          <p>{helpErrorMessage}</p>
        </div>
      );
    }
  }
}

NoResults.propTypes = {
  /**
   * Type is a string input used for displaying a certain html element for No Display
   */
  type: React.PropTypes.string.isRequired,
  /**
   * Error Message is a string passed showing what the error message will say
   */
  errorMessage: React.PropTypes.string.isRequired,
  /**
   * Help Error message is a string passed giving the user some kind of help as to why the are getting the error message
   */
  helpErrorMessage: React.PropTypes.string,
};

export default NoResults;
