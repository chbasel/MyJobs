import React, {PropTypes} from 'react';
import {Col, Row} from 'react-bootstrap';

export default function Card(props) {
  const {title, children} = props;

  return (
    <div className="cardWrapper">
      <Row>
        <Col xs={12}>
          <div className="wrapper-header">
            <h2>{title}</h2>
          </div>
          {children}
        </Col>
      </Row>
    </div>
  );
}

Card.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
};
