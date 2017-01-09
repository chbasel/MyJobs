import React, {PropTypes, Component} from 'react';
import {connect} from 'react-redux';
import {expandStaticUrl} from 'common/assets';


class OutreachCard extends Component {
  constructor() {
    super();
    this.state = {
      showActions: false,
    };
  }

  renderIcons() {
    const {
      hasErrors,
    } = this.props;
    const {
      showActions,
    } = this.state;

    return (
      <div className="tray-items">
        {showActions ?
          <img
          alt="[delete]"
          src={expandStaticUrl('svg/delete.svg')}
          onClick={(event) => {
            this.props.onDel();
            event.stopPropagation();
          }} /> : null}
        {hasErrors ?
          <img
          alt="[error]"
          src={expandStaticUrl('svg/error.svg')} /> : null}
      </div>
    );
  }

  render() {
    const {
      displayText,
      onNav,
      type,
    } = this.props;

    return (
      <div
        className="tray-container progress-card"
        onMouseEnter={() => this.setState({showActions: true})}
        onMouseLeave={() => this.setState({showActions: false})}
        onClick={() => onNav()}>


        <div className="tray-items-left">
          <img
          alt={'[' + type + ']'}
          src={expandStaticUrl('svg/' + type + '-card.svg')} />
        </div>
        {this.renderIcons()}
        <div className="tray-content ellipses">
          <h5>{displayText}</h5>
        </div>
      </div>
    );
  }
}

OutreachCard.propTypes = {
  // Text to show in the card.
  displayText: PropTypes.string.isRequired,
  // User clicked on the card to navigate to the item.
  onNav: PropTypes.func.isRequired,
  onDel: PropTypes.func.isRequired,
  type: PropTypes.string.isRequired,
  hasErrors: PropTypes.bool,
};

export default connect()(OutreachCard);
