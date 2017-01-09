import React from 'react';

class HelpText extends React.Component {
  render() {
    return (
      <div className={'input-error ' + this.props.styleName}>
        {this.props.message}
      </div>
    );
  }
}

HelpText.propTypes = {
  message: React.PropTypes.string.isRequired,
  styleName: React.PropTypes.string.isRequired,
};

HelpText.defaultProps = {
  message: '',
  styleName: '',
};

export default HelpText;
