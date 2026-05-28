dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    implementation("org.apache.commons:commons-math3:3.6.1") // SimpleRegression / Percentile
    implementation("me.paulschwarz:spring-dotenv:4.0.0") // .env 파일 로드 (Python .env 호환)
    runtimeOnly("org.postgresql:postgresql")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

tasks.named<org.springframework.boot.gradle.tasks.bundling.BootJar>("bootJar") {
    archiveFileName.set("ai.jar")
    mainClass.set("com.salesmap.ai.AiApplication")
}

// .env(루트) 로드를 위해 작업 디렉터리를 저장소 루트로 고정
tasks.named<org.springframework.boot.gradle.tasks.run.BootRun>("bootRun") {
    workingDir = rootProject.projectDir
}
