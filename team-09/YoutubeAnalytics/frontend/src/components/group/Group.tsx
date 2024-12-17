import { observer } from "mobx-react-lite";
import "bootstrap/dist/css/bootstrap.css";
import { useState, useEffect, useContext } from "react";
import { Context } from "../..";
import { Col, Row, Button } from "react-bootstrap";
import folder_icon from "../../img/folder.svg";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import ButtonToolbar from "react-bootstrap/ButtonToolbar";

interface Props {
  groups: Array<{ id: number; title: string }>;
  elemsPerRow: number;
  onChooseGroup: (id: number) => void;
}

const Group: React.FC<Props> = (props: Props) => {
  const { store } = useContext(Context);
  const [currentPage, setCurrentPage] = useState(1);

  return (
    <>
      <div
        className="mx-3 border border-primary"
        style={{ width: "100wh", height: "30vh" }}
      >
        {[0, 1].map((row) => (
          <Row xs="auto" className="my-1">
            {props.groups
              .slice(
                2 * props.elemsPerRow * (currentPage - 1) +
                  row * props.elemsPerRow,
                2 * props.elemsPerRow * (currentPage - 1) +
                  props.elemsPerRow * (row + 1)
              )
              .map((group) => (
                <Col key={group.id}>
                  <Button
                    className="mx-3"
                    variant="light"
                    onClick={() => props.onChooseGroup(group.id)}
                  >
                    <img alt="" width="100" height="100" src={folder_icon} />
                    <br />
                    {group.title}
                  </Button>
                </Col>
              ))}
          </Row>
        ))}
      </div>
      <br />
      <ButtonToolbar>
        <ButtonGroup className="mx-3">
          <Button
            onClick={() => {
              if (currentPage !== 1) setCurrentPage(currentPage - 1);
            }}
          >
            prev
          </Button>{" "}
          <Button>{currentPage}</Button>{" "}
          <Button
            onClick={() => {
              if (currentPage * props.elemsPerRow * 2 < props.groups.length)
                setCurrentPage(currentPage + 1);
            }}
          >
            next
          </Button>
        </ButtonGroup>
      </ButtonToolbar>
    </>
  );
};

export default observer(Group);
