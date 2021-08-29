# 23-2nd-Homestagram-backend
## 홈스타그램 프로젝트 소개
- 인테리어 커머스 오늘의 집 클론 프로젝트  
- 프로젝트 기간이 길지 않아 전체가 아닌 일부 기능에 집중해 기획했습니다.
- 개발은 초기 세팅부터 전부 직접 구현했으며, 아래 데모 영상에서 보이는 부분은 실제 사용할 수 있는 서비스 수준으로 개발한 것입니다.

### 개발 인원 및 기간
- 개발기간 : 2021/8/17 ~ 2021/8/27<br>
- 프론트엔드 : [남재현](https://github.com/nam2350), [이지선](https://github.com/ddodam), [최정민](https://github.com/minmin9324)
- 백엔드    : [장호준](https://github.com/bigfanoftim), [송진수](https://github.com/jssong1592)
- [프론트엔드 github 링크](https://github.com/wecode-bootcamp-korea/23-2nd-Homestagram-frontend)

### 프로젝트 선정이유
- 게시글 속 태그를 통하여 커뮤니티와 커머스 기능을 결합한 점에 매력을 느끼고, 이에 모티브를 얻어 프로젝트를 선정하였습니다. 

### 데모 영상/이미지
- https://

## 적용 기술 및 구현 기능
### 적용 기술
- Front-End : HTML5, React, sass, JavaScript 
- Back-End : Python, Django web framework, Bcrypt, PyJWT, MySQL
- Common : AWS(RDS/EC2/S3), KAKAO social login, PayPal API, RESTful API
- Communication: Slack, Trello, Goolge Docs

### 구현 기능
회원가입 & 로그인
- 카카오 소셜 로그인 API를 통한 유효성 검사
- JWT 토큰 발행 후 닉네임 설정, 사이트 내 로그인 수행
- 로그인 데코레이터

유저간 팔로우 기능
- 프론트엔드 요청(버튼 클릭)을 통한 팔로우 리스트 추가/제거
- 마이페이지 팔로우 목록 조회

결제 프로세스
- 프론트엔드 상품 구매 페이지로부터 페이팔 API 결제 정보를 받아 DB에 저장
- 마이페이지 구매내역 조회

메인 페이지 - 게시글 리스트 
- 최신순으로 게시글 정렬
- 게시글 등록 시 유저가 등록한 이미지 속 태그를 클릭하면 해당 제품 상세페이지로 이동
- 댓글 등록/수정/삭제
- 로그인 되어있을 시 게시글 작성자 팔로우 및 게시글 북마크 기능

게시글 작성
- 이미지 등록과 함께 이미지 속 원하는 위치에 해당 제품을 가리키는 태그 등록 기능
- 게시글 등록과 함께 이미지는 AWS S3에 저장, DB에는 해당 이미지 오브젝트 URL 저장


## Reference
- 이 프로젝트는 오늘의 집 사이트를 참조하여 학습목적으로 만들었습니다.
- 실무수준의 프로젝트이지만 학습용으로 만들었기 때문에 이 코드를 활용하여 이득을 취하거나 무단 배포할 경우 법적으로 문제될 수 있습니다.
- 이 프로젝트에서 사용하고 있는 사진 대부분은 위코드에서 구매한 것이므로 해당 프로젝트 외부인이 사용할 수 없습니다.
