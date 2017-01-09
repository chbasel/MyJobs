import React, {PropTypes} from 'react';
import {connect} from 'react-redux';
import Modal from 'react-bootstrap/lib/Modal';
import Button from 'react-bootstrap/lib/Button';


/**
 * Show a confirm modal containing a message and ok/cancel buttons.
 *
 * This component must be in the vdom for the confirmModal method to work.
 *
 * All props are connected so just include the Component.
 * i.e.: <Confirm/>
 */
function Confirm(props) {
  const {show, message, onConfirm} = props;

  return (
    <Modal show={show} onHide={() => onConfirm(false)}>
      <Modal.Body>
      {message}
      </Modal.Body>
      <Modal.Footer>
          <Button
            className="primary"
            onClick={e => {e.preventDefault(); onConfirm(false);}}>
            Cancel
          </Button>
          <Button
            onClick={e => {e.preventDefault(); onConfirm(true);}}>
            Ok
          </Button>
      </Modal.Footer>
    </Modal>
  );
}

Confirm.propTypes = {
  // Should the dialog show right now?
  show: PropTypes.bool.isRequired,
  // What message should it show?
  message: PropTypes.string,
  // Callback for when a button is clicked.
  onConfirm: PropTypes.func,
};

Confirm.defaultProps = {
  message: 'Are you sure?',
};

export default connect(s => ({
  show: s.confirmation.data.show,
  message: s.confirmation.data.message,
  onConfirm: s.confirmation.resolve,
}))(Confirm);
