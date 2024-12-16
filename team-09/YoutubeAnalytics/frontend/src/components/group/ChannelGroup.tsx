import { observer } from "mobx-react-lite";
import "bootstrap/dist/css/bootstrap.css";
import { useState, useContext, useEffect } from "react";
import { Context } from "../..";
import { IChannel } from "../../models/IChannel";
import { Col, Row, Button } from "react-bootstrap";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import ButtonToolbar from "react-bootstrap/ButtonToolbar";
import AddChannelToGroup from "../dialogs/AddChannelToGroup";
import Card from "react-bootstrap/Card";

interface Props {}

const ChannelGroup: React.FC<Props> = (props: Props) => {
  const { store } = useContext(Context);
  const [showAddToGroupDialog, setShowAddToGroupDialog] = useState(false);
  const [channels, setVideos] = useState({} as { [key: string]: IChannel });
  const [currentPage, setCurrentPage] = useState(1);

  const addToGroup = (customUrl: string) => {
    store.addChannelToGroup(customUrl);
  };

  const elemsPerRow = 5;

  useEffect(() => {
    async function fetchdata() {
      if (localStorage.getItem("token")) {
        await store.getChannelsInGroup();

        setVideos(store.channels);
      }
    }
    fetchdata();
  }, []);

  return (
    <>
      <div
        className="mx-3 border border-primary"
        style={{ width: "100wh", height: "75vh" }}
      >
        {[0, 1].map((row) => (
          <Row xs="auto" className="my-1">
            {Object.entries(channels)
              .slice(
                2 * elemsPerRow * (currentPage - 1) + row * elemsPerRow,
                2 * elemsPerRow * (currentPage - 1) + elemsPerRow * (row + 1)
              )
              .map(([channelId, channel]) => (
                <Card className="mx-3 my-1" style={{ width: "18rem" }}>
                  <Card.Body>
                    <Card.Title>{channel.title}</Card.Title>
                    <Card.Text>{channel.description}</Card.Text>
                    <Button variant="primary">Перейти</Button>
                  </Card.Body>
                </Card>
              ))}
          </Row>
        ))}
      </div>

      <Button
        className="mx-3 my-3"
        onClick={() => setShowAddToGroupDialog(true)}
      >
        Добавить канал в группу
      </Button>

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
              if (currentPage * elemsPerRow * 2 < Object.keys(channels).length)
                setCurrentPage(currentPage + 1);
            }}
          >
            next
          </Button>
        </ButtonGroup>
      </ButtonToolbar>

      <AddChannelToGroup
        show={showAddToGroupDialog}
        onChangeShowState={setShowAddToGroupDialog}
        onAddToGroup={addToGroup}
      ></AddChannelToGroup>
    </>
  );
};

export default observer(ChannelGroup);
