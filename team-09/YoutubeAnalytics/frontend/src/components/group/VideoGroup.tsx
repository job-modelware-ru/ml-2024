import { observer } from "mobx-react-lite";
import "bootstrap/dist/css/bootstrap.css";
import { Col, Row, Button } from "react-bootstrap";
import AddVideoToGroup from "../dialogs/AddVideoToGroup";
import { useState, useContext, useEffect } from "react";
import { Context } from "../..";
import Card from "react-bootstrap/Card";
import { IVideo } from "../../models/IVideo";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import ButtonToolbar from "react-bootstrap/ButtonToolbar";
import { useNavigate } from "react-router-dom";

interface Props {}

const VideoGroup: React.FC<Props> = (props: Props) => {
  const { store } = useContext(Context);
  const [showAddToGroupDialog, setShowAddToGroupDialog] = useState(false);
  const [videos, setVideos] = useState({} as { [key: string]: IVideo });
  const [currentPage, setCurrentPage] = useState(1);
  const navigate = useNavigate();
  const addToGroup = (videoId: string) => {
    store.addVideoToGroup(videoId);
  };

  const elemsPerRow = 5;

  useEffect(() => {
    async function fetchdata() {
      if (localStorage.getItem("token")) {
        await store.getVideosInGroup();

        setVideos(store.videos);
      }
    }
    fetchdata();
  }, []);

  return (
    <>
      <div
        className="mx-3 my-3 border border-primary"
        style={{ width: "100wh", height: "75vh" }}
      >
        {[0, 1].map((row) => (
          <Row xs="auto" className="my-1">
            {Object.entries(videos)
              .slice(
                2 * elemsPerRow * (currentPage - 1) + row * elemsPerRow,
                2 * elemsPerRow * (currentPage - 1) + elemsPerRow * (row + 1)
              )
              .map(([videoId, video]) => (
                <Card className="mx-3 my-1" style={{ width: "18rem" }}>
                  <Card.Img
                    variant="top"
                    src={`https://i.ytimg.com/vi/${video.yt_id}/mqdefault.jpg`}
                  />
                  <Card.Body>
                    <Card.Title>{video.title}</Card.Title>
                    <Button variant="primary"
                    onClick={() => navigate("/analysis/" + video.yt_id)}
                    >Перейти</Button>
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
        Добавить видео в группу
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
              if (currentPage * elemsPerRow * 2 < Object.keys(videos).length)
                setCurrentPage(currentPage + 1);
            }}
          >
            next
          </Button>
        </ButtonGroup>
      </ButtonToolbar>

      <AddVideoToGroup
        show={showAddToGroupDialog}
        onChangeShowState={setShowAddToGroupDialog}
        onAddToGroup={addToGroup}
      ></AddVideoToGroup>
    </>
  );
};

export default observer(VideoGroup);
